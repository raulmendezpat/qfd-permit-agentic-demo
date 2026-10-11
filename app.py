import os
from usage_guard import reserve, quota_status
import json
from datetime import datetime, timezone
import streamlit as st

st.set_page_config(page_title='QFD Permit to Light Fire | Demo', page_icon='🔥', layout='wide')

# SYNTHETIC demonstration data. These are NOT QFD authoritative records or rules.
GIS = {
    'Morayfield': {'district':'DEMO-NORTH','property_id':'SYN-101','location':'Morayfield, QLD'},
    'Caboolture': {'district':'DEMO-NORTH','property_id':'SYN-102','location':'Caboolture, QLD'},
    'Woodford': {'district':'DEMO-WEST','property_id':'SYN-103','location':'Woodford, QLD'},
}
OMS = {
    'DEMO-NORTH': {'warden':'Alex Morgan (synthetic)', 'officer_id':'FW-DEMO-01', 'active':True},
    'DEMO-WEST': {'warden':'Sam Taylor (synthetic)', 'officer_id':'FW-DEMO-02', 'active':True},
}
POLICY = {'source':'Synthetic demonstration checklist v1', 'note':'Illustrative workflow checks only; not a QFD policy or legal risk classification.'}

SCENARIOS = {
    'Standard application': {'applicant':'Jordan Lee','email':'jordan@example.test','suburb':'Morayfield','area':3.0,'neighbours':True,'restriction':'clear','description':'Planned vegetation burn on private land.'},
    'Missing information': {'applicant':'Jordan Lee','email':'','suburb':'Caboolture','area':2.0,'neighbours':False,'restriction':'clear','description':''},
    'Restriction / conflict': {'applicant':'Taylor Green','email':'taylor@example.test','suburb':'Woodford','area':5.0,'neighbours':True,'restriction':'conflict','description':'Planned vegetation burn; conflicting synthetic restriction records.'},
}

def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def log(case, actor, action, details):
    case['audit'].append({'timestamp_utc': stamp(), 'actor': actor, 'action': action, 'details': details})

def validate_application(data):
    missing = []
    if not data['applicant'].strip(): missing.append('Applicant name')
    if not data['email'].strip(): missing.append('Email')
    if not data['description'].strip(): missing.append('Burn description')
    if data['area'] <= 0: missing.append('Positive burn area')
    if not data['neighbours']: missing.append('Neighbour notification evidence / follow-up')
    return missing

def lookup_gis_location(suburb):
    return GIS.get(suburb)

def retrieve_fire_warden(district):
    officer = OMS.get(district)
    return officer if officer and officer['active'] else None

def check_restrictions(value):
    return {'result':'unresolved conflict' if value == 'conflict' else 'no conflict in mock dataset',
            'source':'Synthetic restriction dataset (not current restrictions)'}

def retrieve_policy():
    return POLICY

def run_orchestrator(data):
    case = {'data':dict(data), 'status':'Received', 'evidence':{}, 'issues':[], 'audit':[], 'notification':None, 'decision':None}
    log(case,'Orchestrator','CASE_RECEIVED','New synthetic application')
    missing = validate_application(data)
    log(case,'Intake & Guidance','VALIDATE_APPLICATION',f'Missing / unresolved fields: {missing}')
    if missing:
        case['issues'] = missing
        case['status'] = 'Needs information'
        log(case,'Orchestrator','STOP','Incomplete application; no assessment or approval request')
        return case
    geo = lookup_gis_location(data['suburb'])
    log(case,'Property & Compliance','LOOKUP_GIS_LOCATION',f'Location match: {geo}')
    if geo is None:
        case['issues']=['Unable to match location against mock GIS']
        case['status']='Escalated'
        log(case,'Orchestrator','STOP','GIS match unavailable')
        return case
    case['evidence']['mock_gis'] = geo
    officer = retrieve_fire_warden(geo['district'])
    log(case,'Property & Compliance','RETRIEVE_FIRE_WARDEN',f'Mock OMS result: {officer}')
    if officer is None:
        case['issues']=['No active Fire Warden found in mock OMS']
        case['status']='Escalated'
        log(case,'Orchestrator','STOP','Authorised officer not verified')
        return case
    case['evidence']['mock_oms'] = officer
    case['evidence']['mock_policy'] = retrieve_policy()
    restrictions = check_restrictions(data['restriction'])
    case['evidence']['mock_restrictions'] = restrictions
    log(case,'Property & Compliance','CHECK_RESTRICTIONS',str(restrictions))
    if data['restriction'] == 'conflict':
        case['issues']=['Conflicting synthetic restriction records: manual verification required']
        case['status']='Escalated'
        log(case,'Orchestrator','STOP','Conflict detected; blocked before approval routing')
        return case
    case['status']='Awaiting Fire Warden review'
    log(case,'Orchestrator','REQUEST_APPROVAL',f"Route draft assessment to {officer['officer_id']}")
    return case

def human_decision(case, decision, role):
    if case['status'] != 'Awaiting Fire Warden review':
        raise ValueError('Not eligible for decision; resolve issues first')
    if role not in ('Fire Warden (demo)','Chief Fire Warden (demo)'):
        raise ValueError('Demo role not authorised')
    case['decision']={'decision':decision,'role':role,'timestamp_utc':stamp()}
    case['status']='Approved (demo)' if decision == 'Approve' else 'Rejected (demo)'
    log(case, role,'HUMAN_DECISION',decision)
    if decision == 'Approve':
        case['notification']='Ready to simulate downstream update'
    else:
        case['notification']='No downstream activation; rejection recorded'
    return case

def notify_downstream_systems(case, simulate_failure):
    if case['status'] != 'Approved (demo)':
        raise ValueError('Human approval is required before downstream update')
    if simulate_failure:
        case['notification']='FAILED — queued for manual intervention (simulation)'
        log(case,'Comms & Integration','MOCK_UPDATE_FAILED','ESCAD/OMS synthetic outage; no success claimed')
    else:
        case['notification']='SUCCESS — synthetic ESCAD/OMS records updated'
        log(case,'Comms & Integration','MOCK_UPDATE_SUCCESS','Only local synthetic state updated; no external request')

st.title('🔥 Permit to Light Fire — Agentic Prototype')
st.caption('Education-only prototype • Synthetic GIS / OMS / restrictions • No connection to QFD systems • Deterministic safety gates + optional real LLM agents')
st.warning('All records, officers, restrictions and decisions are fictional. This application must not be used for real fire-permit decisions.', icon='⚠️')

if 'case' not in st.session_state: st.session_state.case = None
if 'llm_assessment' not in st.session_state: st.session_state.llm_assessment = None
if 'llm_notification' not in st.session_state: st.session_state.llm_notification = None
if 'llm_events' not in st.session_state: st.session_state.llm_events = []
if 'llm_calls' not in st.session_state: st.session_state.llm_calls = {'assessment':0,'notification':0}
try:
    if not os.getenv('OPENAI_API_KEY') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
except (FileNotFoundError, KeyError):
    pass
with st.sidebar:
    st.header('Demonstration controls')
    scenario = st.selectbox('Load test scenario', list(SCENARIOS))
    st.caption('Choose a scenario, then process it using the application form.')
    used, total = quota_status()
    st.caption(f'Shared instance AI quota: {used}/{total} calls today (UTC). Resets on server restart.')
    st.markdown('**Agent architecture**')
    st.write('1. Orchestrator\n\n2. Intake & Guidance\n\n3. Property & Compliance\n\n4. Comms & Integration')
    if st.button('Clear current case', use_container_width=True):
        st.session_state.case = None
        st.session_state.llm_assessment = None
        st.session_state.llm_notification = None
        st.session_state.llm_events = []
        st.rerun()

input_tab, review_tab, audit_tab = st.tabs(['1 · Application & agent run','2 · Human review & integration','3 · Evidence & audit trail'])
with input_tab:
    st.subheader('Submit synthetic application')
    data = SCENARIOS[scenario]
    with st.form('permit_form'):
        a,b = st.columns(2)
        with a:
            applicant = st.text_input('Applicant name', value=data['applicant'])
            email = st.text_input('Email', value=data['email'])
            suburb = st.selectbox('Suburb (synthetic GIS match)',list(GIS),index=list(GIS).index(data['suburb']))
        with b:
            area = st.number_input('Planned burn area (ha)',min_value=0.0,max_value=10000.0,value=float(data['area']),step=0.5)
            neighbours = st.checkbox('Neighbour contact evidence provided (demo field)',value=data['neighbours'])
            restriction = st.selectbox('Mock restriction response', ['clear','conflict'],index=0 if data['restriction']=='clear' else 1)
        description = st.text_area('Proposed burn description',value=data['description'])
        submitted = st.form_submit_button('Run orchestrator and specialist agents',type='primary')
    if submitted:
        payload = {'applicant':applicant,'email':email,'suburb':suburb,'area':area,'neighbours':neighbours,'restriction':restriction,'description':description}
        st.session_state.case = run_orchestrator(payload)
        st.session_state.llm_assessment = None
        st.session_state.llm_notification = None
        st.session_state.llm_events = []
    case = st.session_state.case
    if case:
        st.subheader('Agent execution result')
        st.info(f"Case status: {case['status']}")
        if case['issues']: st.error('Unresolved items: ' + '; '.join(case['issues']))
        else: st.success('Checks completed using synthetic evidence. A human decision is required.')
        st.dataframe(case['audit'],use_container_width=True,hide_index=True)
        st.markdown('### Optional real LLM multi-agent assessment')
        st.caption('Uses OpenAI Agents SDK with an orchestrator and two LLM specialists. Read-only mock tools; cannot alter case status or bypass approval.')
        st.caption('Maximum one LLM assessment per browser session; shared best-effort daily quota. Deterministic demo remains available.')
        if not os.environ.get('OPENAI_API_KEY'):
            st.warning('OPENAI_API_KEY not configured. Deterministic workflow remains available.')
        else:
            if st.button('Run real LLM agents (read-only)', disabled=st.session_state.llm_calls['assessment']>=1):
                ok, note = reserve('assessment')
                if not ok:
                    st.warning(note)
                else:
                    st.session_state.llm_calls['assessment'] += 1
                    try:
                        from llm_agents import run_llm_assessment
                        with st.spinner('Running real LLM agents and read-only synthetic tools...'):
                            result = run_llm_assessment(case['data'])
                        st.session_state.llm_assessment = result['text']
                        st.session_state.llm_events.extend(result['events'])
                        log(case,'LLM Orchestrator','LLM_ADVISORY_ONLY','Read-only advisory generated; no workflow status changed')
                    except Exception as exc:
                        st.error(f'LLM request failed ({type(exc).__name__}). No workflow changes made.')
            if st.session_state.llm_assessment:
                st.markdown('**LLM draft recommendation — not an official decision**')
                st.write(st.session_state.llm_assessment)
                st.info('Evidence limitation ≠ detected conflict. Mock status clear is not a verified real-world restriction status.')
            if st.session_state.llm_events:
                with st.expander('Real SDK agent/tool execution events'):
                    st.dataframe(st.session_state.llm_events,use_container_width=True,hide_index=True)

with review_tab:
    case = st.session_state.case
    if not case: st.info('Run an application in the first tab.')
    else:
        st.subheader('Human-in-the-loop control')
        st.write('Current status:', case['status'])
        if case['status']=='Awaiting Fire Warden review':
            st.json(case['evidence'],expanded=False)
            role = st.selectbox('Simulated authorised role', ['Fire Warden (demo)','Chief Fire Warden (demo)'])
            c1,c2 = st.columns(2)
            with c1:
                if st.button('Approve (human action)',type='primary',use_container_width=True):
                    human_decision(case,'Approve',role)
                    st.rerun()
            with c2:
                if st.button('Reject (human action)',use_container_width=True):
                    human_decision(case,'Reject',role)
                    st.rerun()
        elif case['status'] in ('Needs information','Escalated'):
            st.error('Automated workflow stopped. Resolve or verify the case externally before proceeding.')
        elif case['status']=='Rejected (demo)': st.warning('Human rejection recorded. Downstream activation blocked.')
        elif case['status']=='Approved (demo)':
            st.success('Synthetic human approval recorded.')
            failure = st.checkbox('Simulate ESCAD/OMS integration failure')
            if st.button('Run mock downstream integration'):
                notify_downstream_systems(case,failure)
                st.rerun()
            st.markdown('#### Optional communications LLM agent')
            st.caption('Generates an unsent draft only. The existing mock integration remains a separate human-triggered button.')
            if st.button('Draft stakeholder message with LLM',disabled=st.session_state.llm_calls['notification']>=1):
                if not os.environ.get('OPENAI_API_KEY'):
                    st.error('OPENAI_API_KEY missing')
                else:
                    ok, note = reserve('notification')
                    if not ok:
                        st.warning(note)
                    else:
                        st.session_state.llm_calls['notification'] += 1
                        try:
                            from llm_agents import draft_llm_notification
                            with st.spinner('Generating unsent draft...'):
                                result = draft_llm_notification(case)
                            st.session_state.llm_notification = result['text']
                            st.session_state.llm_events.extend(result['events'])
                            log(case,'Comms LLM','LLM_DRAFT_ONLY','Unsent draft created; no external update')
                        except Exception as exc:
                            st.error(f'LLM draft failed ({type(exc).__name__}); no downstream action taken')
            if st.session_state.llm_notification:
                st.text_area('Unsent synthetic notification draft',st.session_state.llm_notification,height=160)
        if case.get('notification'): st.info(case['notification'])

with audit_tab:
    case = st.session_state.case
    if not case: st.info('No case has been processed yet.')
    else:
        st.subheader('Retrieved synthetic evidence')
        st.json(case['evidence'])
        st.subheader('Human decision')
        st.json(case['decision'])
        st.subheader('Real LLM agent/tool events')
        if st.session_state.llm_events:
            st.dataframe(st.session_state.llm_events,use_container_width=True,hide_index=True)
        else:
            st.caption('No real LLM calls in this session yet.')
        st.subheader('Audit history')
        st.dataframe(case['audit'],use_container_width=True,hide_index=True)
        st.download_button('Download case and audit JSON',data=json.dumps(case,indent=2),file_name='synthetic_case_audit.json',mime='application/json')
