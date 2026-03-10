from typing import Any, Dict

from bson import ObjectId

from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.db.connection import get_db
from app.utils.printcolors import Colors


async def fetch_campaign_brief_node(state: WhatsappNegotiationState):
    """
    Enrich the negotiation state with the campaign brief (if available).

    - If state already has `campaign_brief`, this node is a no-op.
    - If there's no campaign_id or no brief_id on the campaign, it safely returns.
    """
    print(f"{Colors.GREEN}Entering fetch_campaign_brief_node")
    print("--------------------------------")

    # Skip if already present
    if state.get("campaign_brief") is not None:
        print(
            f"{Colors.YELLOW}[fetch_campaign_brief_node] campaign_brief already present on state; skipping DB fetch"
        )
        print("--------------------------------")
        return state

    try:
        db = get_db()
        # 1) Resolve campaign_id from influencer_id via campaign_influencers
        influencer_id = state.get("influencer_id")
        if not influencer_id:
            print(
                f"{Colors.YELLOW}[fetch_campaign_brief_node] No influencer_id on state; cannot resolve campaign"
            )
            print("--------------------------------")
            return state

        try:
            influencer_object_id = ObjectId(str(influencer_id))
        except Exception:
            print(
                f"{Colors.RED}[fetch_campaign_brief_node] Invalid influencer_id on state: {influencer_id}"
            )
            print("--------------------------------")
            return state

        campaign_influencers_collection = db.get_collection("campaign_influencers")
        influencer_doc: Dict[str, Any] = await campaign_influencers_collection.find_one(
            {"_id": influencer_object_id}
        )

        if not influencer_doc:
            print(
                f"{Colors.YELLOW}[fetch_campaign_brief_node] No campaign_influencer found for id={influencer_object_id}"
            )
            print("--------------------------------")
            return state

        campaign_id = influencer_doc.get("campaign_id")
        if not campaign_id:
            print(
                f"{Colors.YELLOW}[fetch_campaign_brief_node] Influencer has no campaign_id; skipping brief fetch"
            )
            print("--------------------------------")
            return state

        try:
            campaign_object_id = (
                campaign_id
                if isinstance(campaign_id, ObjectId)
                else ObjectId(str(campaign_id))
            )
        except Exception:
            print(
                f"{Colors.RED}[fetch_campaign_brief_node] Invalid campaign_id on influencer doc: {campaign_id}"
            )
            print("--------------------------------")
            return state

        # 2) Fetch campaign and its brief_id
        campaigns_collection = db.get_collection("campaigns")
        campaign_doc: Dict[str, Any] = await campaigns_collection.find_one(
            {"_id": campaign_object_id}
        )

        if not campaign_doc:
            print(
                f"{Colors.YELLOW}[fetch_campaign_brief_node] No campaign found for id={campaign_object_id}"
            )
            print("--------------------------------")
            return state

        brief_id = campaign_doc.get("brief_id")
        if not brief_id:
            print(
                f"{Colors.YELLOW}[fetch_campaign_brief_node] Campaign has no brief_id; skipping brief fetch"
            )
            print("--------------------------------")
            return state
        briefs_collection = db.get_collection("CampaignBriefGeneration")
        brief_doc: Dict[str, Any] = await briefs_collection.find_one(
            {"_id": str(brief_id)}
        )
        if not brief_doc:
            print(
                f"{Colors.YELLOW}[fetch_campaign_brief_node] No brief found for id={brief_id}"
            )
            print("--------------------------------")
            return state

        # The actual brief content is stored under "response"
        brief_payload = brief_doc.get("response") or {}
        state["campaign_brief"] = brief_payload

        print(
            f"{Colors.CYAN}[fetch_campaign_brief_node] Attached campaign_brief to state for campaign_id={campaign_id}"
        )
        print("--------------------------------")
        return state

    except Exception as e:
        print(f"{Colors.RED}[fetch_campaign_brief_node] Failed to fetch brief: {e}")
        print("--------------------------------")
        return state

