import logging
from datetime import datetime, timezone

from mongomock_motor import AsyncMongoMockClient

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception:
    AsyncIOMotorClient = None

from app.core.config import settings
from app.core.security import hash_password


logger = logging.getLogger("uvicorn")


class DatabaseManager:
    client = None
    db = None
    is_mock: bool = False

    @classmethod
    async def connect_db(cls):
        """
        Connect to live MongoDB when MONGODB_URL is configured.
        Otherwise, use the in-memory MongoDB fallback.
        """

        if settings.MONGODB_URL and AsyncIOMotorClient is not None:
            try:
                test_client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    serverSelectionTimeoutMS=2000,
                )

                await test_client.admin.command("ping")

                cls.client = test_client
                cls.db = cls.client[settings.DATABASE_NAME]
                cls.is_mock = False

                logger.info(
                    f"Connected to live MongoDB at {settings.MONGODB_URL}"
                )

                await cls.seed_default_data()
                return

            except Exception as error:
                logger.warning(
                    f"Could not connect to live MongoDB: {error}. "
                    "Falling back to in-memory MongoDB."
                )

        elif settings.MONGODB_URL and AsyncIOMotorClient is None:
            logger.warning(
                "motor.motor_asyncio not available; "
                "using in-memory MongoDB."
            )

        cls.client = AsyncMongoMockClient()
        cls.db = cls.client[settings.DATABASE_NAME]
        cls.is_mock = True

        logger.info(
            "Using in-memory MongoDB fallback (AsyncMongoMockClient)."
        )

        await cls.seed_default_data()

    @classmethod
    async def close_db(cls):
        """Close the live MongoDB connection."""

        if cls.client and not cls.is_mock:
            cls.client.close()

    @classmethod
    async def seed_default_data(cls):
        """Insert default demo data when the database is empty."""

        if cls.db is None:
            return

        users_col = cls.db["users"]

        existing_user = await users_col.find_one(
            {"email": "demo@infosys.com"}
        )

        if existing_user:
            return

        demo_user_id = "user_demo_001"

        await users_col.insert_one(
            {
                "_id": demo_user_id,
                "email": "demo@infosys.com",
                "full_name": "Infosys Research Analyst",
                "hashed_password": hash_password("password123"),
                "role": "Senior Financial Analyst",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        # --------------------------------------------------
        # SEED DEFAULT WORKSPACES
        # --------------------------------------------------

        workspaces_col = cls.db["workspaces"]

        workspace_id_1 = "ws_demo_001"
        workspace_id_2 = "ws_demo_002"

        await workspaces_col.insert_many(
            [
                {
                    "_id": workspace_id_1,
                    "name": "Infosys FY24 Financial & Risk Assessment",
                    "description": (
                        "Comprehensive multi-agent deep dive into "
                        "Infosys annual reports, revenue trends, "
                        "and audit flags."
                    ),
                    "user_id": demo_user_id,
                    "created_at": "2026-08-01T10:00:00Z",
                    "updated_at": "2026-08-03T18:30:00Z",
                    "documents_count": 3,
                },
                {
                    "_id": workspace_id_2,
                    "name": "Big Tech Peer Comparison (AAPL vs MSFT)",
                    "description": (
                        "Side-by-side benchmarking of EBIT margins, "
                        "cloud growth, and debt-to-equity ratios."
                    ),
                    "user_id": demo_user_id,
                    "created_at": "2026-08-02T14:15:00Z",
                    "updated_at": "2026-08-03T12:00:00Z",
                    "documents_count": 2,
                },
            ]
        )

        # --------------------------------------------------
        # SEED DEFAULT DOCUMENTS
        # --------------------------------------------------

        docs_col = cls.db["documents"]

        await docs_col.insert_many(
            [
                {
                    "_id": "doc_seed_001",
                    "title": "Infosys Limited FY2024 Annual Report.pdf",
                    "company_name": "Infosys Limited",
                    "filing_type": "Annual Report (20-F)",
                    "fiscal_year": 2024,
                    "workspace_id": workspace_id_1,
                    "user_id": demo_user_id,
                    "file_path": (
                        "seed/infosys_fy24_annual_report.pdf"
                    ),
                    "file_size": 4820100,
                    "status": "INDEXED",
                    "is_seed": True,
                    "chunks_count": 142,
                    "uploaded_at": "2026-08-01T10:05:00Z",
                },
                {
                    "_id": "doc_seed_002",
                    "title": (
                        "Infosys FY24 Q4 Earnings "
                        "Call Transcript.pdf"
                    ),
                    "company_name": "Infosys Limited",
                    "filing_type": "Earnings Transcript",
                    "fiscal_year": 2024,
                    "workspace_id": workspace_id_1,
                    "user_id": demo_user_id,
                    "file_path": (
                        "seed/infosys_fy24_q4_transcript.pdf"
                    ),
                    "file_size": 1104000,
                    "status": "INDEXED",
                    "is_seed": True,
                    "chunks_count": 68,
                    "uploaded_at": "2026-08-01T11:20:00Z",
                },
                {
                    "_id": "doc_seed_003",
                    "title": "Apple Inc. FY2023 Form 10-K.pdf",
                    "company_name": "Apple Inc.",
                    "filing_type": "10-K Filing",
                    "fiscal_year": 2023,
                    "workspace_id": workspace_id_2,
                    "user_id": demo_user_id,
                    "file_path": "seed/aapl_fy23_10k.pdf",
                    "file_size": 5912000,
                    "status": "INDEXED",
                    "is_seed": True,
                    "chunks_count": 210,
                    "uploaded_at": "2026-08-02T14:20:00Z",
                },
                {
                    "_id": "doc_seed_004",
                    "title": (
                        "Microsoft Corp. FY2023 Form 10-K.pdf"
                    ),
                    "company_name": "Microsoft Corporation",
                    "filing_type": "10-K Filing",
                    "fiscal_year": 2023,
                    "workspace_id": workspace_id_2,
                    "user_id": demo_user_id,
                    "file_path": "seed/msft_fy23_10k.pdf",
                    "file_size": 6120000,
                    "status": "INDEXED",
                    "is_seed": True,
                    "chunks_count": 225,
                    "uploaded_at": "2026-08-02T14:30:00Z",
                },
            ]
        )

        # --------------------------------------------------
        # SEED DEFAULT ANALYST REPORTS
        # --------------------------------------------------

        reports_col = cls.db["reports"]

        await reports_col.insert_many(
            [
                {
                    "_id": "rep_seed_001",
                    "title": (
                        "Infosys FY2024 Comprehensive Financial "
                        "& Risk Analyst Report"
                    ),
                    "workspace_id": workspace_id_1,
                    "user_id": demo_user_id,
                    "company_name": "Infosys Limited",
                    "summary": (
                        "Full multi-agent research evaluation of "
                        "Infosys FY24 performance, EBIT margin "
                        "resiliency, debt profile, and auditor "
                        "observations."
                    ),
                    "status": "COMPLETED",
                    "created_at": "2026-08-03T15:00:00Z",
                    "sections": {
                        "executive_summary": (
                            "Infosys FY24 demonstrated disciplined "
                            "operational execution amidst macro-economic "
                            "headwinds in North American banking and "
                            "telecom verticals. Total revenue reached "
                            "$18,562M (+1.9% YoY in USD terms), "
                            "underpinned by large deal wins totaling "
                            "$17.7B in TCV. Operating margins remained "
                            "resilient at 20.7%, supported by Project "
                            "Maximus efficiency initiatives."
                        ),
                        "key_financials": [
                            {
                                "metric": "Revenue (USD)",
                                "fy23": "$18,212M",
                                "fy24": "$18,562M",
                                "yoy_change": "+1.9%",
                                "status": "Positive",
                            },
                            {
                                "metric": "Operating Margin (EBIT)",
                                "fy23": "21.0%",
                                "fy24": "20.7%",
                                "yoy_change": "-30 bps",
                                "status": "Neutral",
                            },
                            {
                                "metric": "Free Cash Flow (FCF)",
                                "fy23": "$2,480M",
                                "fy24": "$2,890M",
                                "yoy_change": "+16.5%",
                                "status": "Positive",
                            },
                            {
                                "metric": "Debt to Equity Ratio",
                                "fy23": "0.08x",
                                "fy24": "0.07x",
                                "yoy_change": "-0.01x",
                                "status": "Positive",
                            },
                            {
                                "metric": "EPS (Diluted USD)",
                                "fy23": "$0.71",
                                "fy24": "$0.73",
                                "yoy_change": "+2.8%",
                                "status": "Positive",
                            },
                        ],
                        "red_flags": [
                            {
                                "severity": "Medium",
                                "title": (
                                    "North American Financial Services "
                                    "Discretionary Spend Softness"
                                ),
                                "description": (
                                    "Client budget scrutiny in BFS "
                                    "vertical caused delayed deal "
                                    "conversions and slower ramp-up "
                                    "of discretionary consulting "
                                    "engagements."
                                ),
                                "citation": (
                                    "FY24 Annual Report p. 44"
                                ),
                            },
                            {
                                "severity": "Low",
                                "title": (
                                    "Subcontractor Cost Fluctuations"
                                ),
                                "description": (
                                    "While subcontractor costs reduced "
                                    "to 7.4% of revenue in Q4, offshore "
                                    "wage hikes may compress near-term "
                                    "margins."
                                ),
                                "citation": (
                                    "FY24 Q4 Transcript p. 12"
                                ),
                            },
                            {
                                "severity": "Info",
                                "title": (
                                    "Auditor Qualification Check"
                                ),
                                "description": (
                                    "No auditor qualifications or "
                                    "going-concern modifications "
                                    "detected in Deloitte Haskins & "
                                    "Sells LLP report."
                                ),
                                "citation": (
                                    "FY24 Annual Report p. 182"
                                ),
                            },
                        ],
                        "comparison": [
                            {
                                "company": "Infosys Limited",
                                "revenue": "$18.56B",
                                "ebit_margin": "20.7%",
                                "roe": "31.4%",
                                "fcf_conversion": "82%",
                            },
                            {
                                "company": "TCS Limited",
                                "revenue": "$29.08B",
                                "ebit_margin": "24.6%",
                                "roe": "51.5%",
                                "fcf_conversion": "89%",
                            },
                            {
                                "company": "Wipro Limited",
                                "revenue": "$10.81B",
                                "ebit_margin": "16.1%",
                                "roe": "15.2%",
                                "fcf_conversion": "78%",
                            },
                        ],
                        "outlook": (
                            "We maintain a positive outlook on Infosys "
                            "given strong deal TCV ($17.7B) and "
                            "expanding GenAI service offerings through "
                            "Infosys Topaz. Near-term focus remains on "
                            "utilization improvements and discretionary "
                            "demand recovery."
                        ),
                    },
                },
                {
                    "_id": "rep_seed_002",
                    "title": (
                        "Apple vs Microsoft Enterprise AI & Cloud "
                        "Growth Benchmarking Report"
                    ),
                    "workspace_id": workspace_id_2,
                    "user_id": demo_user_id,
                    "company_name": "Multi-Company Benchmark",
                    "summary": (
                        "Comparative analysis of Microsoft Intelligent "
                        "Cloud acceleration versus Apple Services "
                        "margin expansion in FY23."
                    ),
                    "status": "COMPLETED",
                    "created_at": "2026-08-03T17:30:00Z",
                    "sections": {
                        "executive_summary": (
                            "Microsoft continues to outpace in cloud "
                            "revenue growth (+18% YoY in Intelligent "
                            "Cloud), while Apple demonstrates "
                            "exceptional gross margin strength in "
                            "Services (70.8%). Both balance sheets "
                            "remain robust with AA+/AAA credit ratings."
                        ),
                        "key_financials": [
                            {
                                "metric": "Revenue",
                                "fy23": (
                                    "AAPL: $383.3B / MSFT: $211.9B"
                                ),
                                "fy24": "N/A",
                                "yoy_change": (
                                    "AAPL (-2.8%) / MSFT (+6.9%)"
                                ),
                                "status": "Neutral",
                            },
                            {
                                "metric": "Operating Margin",
                                "fy23": (
                                    "AAPL: 29.8% / MSFT: 41.8%"
                                ),
                                "fy24": "N/A",
                                "yoy_change": "MSFT +150 bps",
                                "status": "Positive",
                            },
                        ],
                        "red_flags": [],
                        "comparison": [
                            {
                                "company": "Apple Inc.",
                                "revenue": "$383.29B",
                                "ebit_margin": "29.8%",
                                "roe": "171.9%",
                                "fcf_conversion": "102%",
                            },
                            {
                                "company": "Microsoft Corp.",
                                "revenue": "$211.91B",
                                "ebit_margin": "41.8%",
                                "roe": "38.8%",
                                "fcf_conversion": "81%",
                            },
                        ],
                        "outlook": (
                            "High strategic value in Microsoft's Azure "
                            "+ OpenAI integration; Apple ecosystem "
                            "monetization remains defensible."
                        ),
                    },
                },
            ]
        )

        logger.info(
            "Default seed user, workspaces, documents, and "
            "reports inserted successfully!"
        )


db_manager = DatabaseManager()


def get_db():
    return db_manager.db