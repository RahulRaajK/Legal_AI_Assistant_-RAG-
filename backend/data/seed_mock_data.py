"""Seed mock cases, chats, and other domain objects for testing."""
import json
from datetime import datetime, timedelta
from sqlalchemy import select
from backend.models.user import User
from backend.models.case import Case, CaseDocument
from backend.models.document import ChatSession, ChatMessage
from backend.ingestion.pipeline import ingestion_pipeline
import os

async def seed_mock_domain_data(db):
    print("🌱 Seeding Mock Domain Data (Cases, Chats)...")
    
    # Get mock users
    judge_user = await db.execute(select(User).where(User.email == "judge@india.gov.in"))
    judge_user = judge_user.scalar_one_or_none()
    
    lawyer_user = await db.execute(select(User).where(User.email == "lawyer@india.gov.in"))
    lawyer_user = lawyer_user.scalar_one_or_none()
    
    if not judge_user or not lawyer_user:
        print("⚠️ Missing mock users. Cannot seed mock domain data.")
        return

    # 1. Seed Mock Cases (assigned to the lawyer layer)
    existing_cases = await db.execute(select(Case).where(Case.user_id == lawyer_user.id))
    if len(existing_cases.scalars().all()) == 0:
        now = datetime.utcnow()
        cases = [
            Case(
                user_id=lawyer_user.id,
                case_title="State vs. Ramesh Kumar (Fraud & Forgery)",
                case_number="CR/2026/0441",
                fir_number="FIR-DL-023-2025",
                case_code="CNR-DL01-1234-2026",
                case_type="Criminal",
                act="Bharatiya Nyaya Sanhita, 2023",
                petitioner="State of Delhi",
                respondent="Ramesh Kumar",
                advocate_name="Advocate Sharma",
                court_name="District Court Saket",
                registration_number="REG-99120",
                judge_name="Honorable Judge",
                description="The respondent is accused of forging corporate documents to secure a bank loan of ₹2.5 Crores.",
                facts="1. The respondent applied for a commercial loan at State Bank of India.\n2. Several collateral title deeds submitted were alleged to be fabricated.\n3. Bank auditor discovered discrepancies during a routine survey.",
                status="active",
                priority="high",
                filing_date=now - timedelta(days=45),
                next_hearing_date=now + timedelta(days=12),
                hearing_time="10:30 AM",
                petitioner_attendance="Present",
                respondent_attendance="Unknown"
            ),
            Case(
                user_id=lawyer_user.id,
                case_title="State vs. Amit Patel (Cyber Ransomware & Data Theft)",
                case_number="CY/2026/0204",
                case_code="CNR-GJ04-9988-2026",
                case_type="Criminal / Cyber Crime",
                act="Information Technology Act, 2000 & BNS, 2023",
                petitioner="State of Gujarat (Cyber Cell)",
                respondent="Amit Patel",
                advocate_name="Advocate Sharma",
                court_name="District Court Ahmedabad",
                registration_number="REG-77002",
                judge_name="Honorable Judge",
                description="The respondent is accused of orchestrating a ransomware attack on a local hospital network and stealing patient data.",
                facts="1. Ransomware deployed via phishing email on Feb 10, 2026.\n2. Over 500 patient records were encrypted and exfiltrated.\n3. IP logs trace the attack origin to the respondent's registered internet connection.",
                status="pending",
                priority="high",
                filing_date=now - timedelta(days=20),
                next_hearing_date=now + timedelta(days=5),
                hearing_time="2:00 PM",
                petitioner_attendance="Present",
                respondent_attendance="Present"
            ),
            Case(
                user_id=lawyer_user.id,
                case_title="Ramesh Builders vs. State Authority (Land Acquisition)",
                case_number="WP/2026/0112",
                case_code="CNR-KA03-7788-2026",
                case_type="Writ Petition",
                act="Constitution of India (Article 226)",
                petitioner="Ramesh Builders Pvt Ltd",
                respondent="State Urban Development Authority",
                advocate_name="Advocate Sharma",
                court_name="High Court of Karnataka",
                registration_number="REG-33201",
                judge_name="Honorable Judge",
                description="Challenging the arbitrary acquisition of 5 acres of commercial land for a proposed highway project without fair compensation.",
                facts="1. Plot acquired via notification issued in Jan 2026.\n2. Compensation offered is 40% below market circle rate.\n3. Petitioner seeks a stay on the demolition.",
                status="active",
                priority="high",
                filing_date=now - timedelta(days=10),
                next_hearing_date=now + timedelta(days=2),
                hearing_time="11:15 AM",
                petitioner_attendance="Unknown",
                respondent_attendance="Unknown"
            )
        ]
        db.add_all(cases)
        await db.commit()
        
        first_case = cases[0]
        await db.refresh(first_case)
        print("✅ Seeded 3 Mock Cases for the Lawyer.")

        mock_docs_dir = os.path.join(os.path.dirname(__file__), "mock_docs")
        
        docs = [
            CaseDocument(
                case_id=first_case.id,
                filename="FIR_Copy_DL023.pdf",
                file_path=os.path.join(mock_docs_dir, "FIR_Copy_DL023.pdf"),
                file_type="pdf",
                document_type="fir",
                submitted_by="petitioner",
                admissibility_status="valid",
                is_processed="completed"
            ),
            CaseDocument(
                case_id=first_case.id,
                filename="Bank_Audit_Report.pdf",
                file_path=os.path.join(mock_docs_dir, "Bank_Audit_Report.pdf"),
                file_type="pdf",
                document_type="evidence",
                submitted_by="petitioner",
                admissibility_status="pending",
                is_processed="completed"
            ),
            CaseDocument(
                case_id=first_case.id,
                filename="Defense_Witness_Statement_1.pdf",
                file_path=os.path.join(mock_docs_dir, "Defense_Witness_Statement_1.pdf"),
                file_type="pdf",
                document_type="witness_statement",
                submitted_by="respondent",
                admissibility_status="pending",
                is_processed="completed"
            )
        ]
        db.add_all(docs)
        await db.commit()
        
        # Ingest the mock document PDFs into the Vector Store
        print("🔍 Extracting Valid Mock PDFs directly into FAISS Vector Store...")
        for doc in docs:
            if os.path.exists(doc.file_path):
                metadata = {
                    "content_type": "uploaded_document",
                    "document_type": doc.document_type,
                    "source_name": "mock_seeder",
                    "act_name": doc.filename,
                }
                res = ingestion_pipeline.ingest_file(doc.file_path, metadata)
                doc.chunk_count = res.get("chunks_stored", 0)
        await db.commit()
        print("✅ Seeded Mock Documents for the first case with FAISS extracted context.")

    # 2. Seed Mock Chat Session
    existing_chats = await db.execute(select(ChatSession).where(ChatSession.user_id == lawyer_user.id))
    if len(existing_chats.scalars().all()) == 0:
        chat = ChatSession(
            user_id=lawyer_user.id,
            title="Analysis of Defamation Precedents (Mock)",
            context_mode="general",
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        
        msgs = [
            ChatMessage(session_id=chat.id, role="user", content="Can you outline the supreme court precedents for civil defamation vs criminal defamation?"),
            ChatMessage(session_id=chat.id, role="assistant", content="In India, defamation is both a civil wrong (tort) and a criminal offence (Section 499 of the IPC / Section 356 of BNS). \n\n**Key Precedents:**\n1. **Subramanian Swamy v. Union of India (2016)**: The Supreme Court upheld the constitutional validity of criminal defamation, ruling it does not violate the right to free speech under Article 19(1)(a). The court noted that reputation is an integral part of Article 21 (Right to Life).\n2. **R. Rajagopal v. State of T.N. (1994)**: Known as the Auto Shankar case, the court held that public officials cannot sue for defamation for acts related to their official duties unless they prove 'actual malice' or reckless disregard for the truth.")
        ]
        db.add_all(msgs)
        await db.commit()
        print("✅ Seeded Mock Chat Session for the Lawyer.")
