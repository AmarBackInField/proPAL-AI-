import asyncio
import time
from dotenv import load_dotenv
from livekit import api
from livekit.protocol.sip import CreateSIPParticipantRequest

load_dotenv()

async def make_outbound_call():
    """
    Make an outbound call - run this after your agent is running
    """
    print("📞Initiating outbound call...")
    print("⏳Connecting to LiveKit API...")
    
    livekit_api = api.LiveKitAPI()
    
    # Configuration
    PHONE_NUMBER = "+919911062767"  # Add the no. which is verified in our twilio account
    ROOM_NAME = "my-assistant-room"  # Use a consistent room name
    
    request = CreateSIPParticipantRequest(
        sip_trunk_id="ST_xrzim78pNWRG",  # It is provided from the outbound_call.json
        sip_call_to=PHONE_NUMBER,
        room_name=ROOM_NAME,
        participant_identity="sip-caller",
        participant_name="Phone Caller",
        krisp_enabled=True,
        wait_until_answered=True
    )
    
    try:
        print(f"📱 Calling {PHONE_NUMBER}...")
        print(f"🏠 Room: {ROOM_NAME}")
        
        start_time = time.time()
        participant = await livekit_api.sip.create_sip_participant(request)
        connection_time = time.time() - start_time
        
        print(f"* Connection established in {connection_time:.2f} seconds")
        print(f"* Participant ID: {participant.participant_id}")
        print(f"* SIP Call ID: {participant.sip_call_id}")
        print(f"* Room: {participant.room_name}")
        print("-" * 50)
        print("* The AI assistant should now be speaking to the caller")
        print("* Metrics are being logged in real-time")
        
    except Exception as e:
        print(f" Error creating SIP participant: {e}")
        print(" Make sure:")
        print("   1. Your agent is running first")
        print("   2. SIP trunk ID is correct")
        print("   3. Phone number format is correct")
        print("   4. LiveKit credentials are set")
    finally:
        await livekit_api.aclose()

if __name__ == "__main__":
    print(" ProPAL AI - Outbound Call Initiator")
    print("=" * 50)
    asyncio.run(make_outbound_call())