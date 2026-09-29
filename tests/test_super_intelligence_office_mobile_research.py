"""
Comprehensive Verification Suite for KOSIF Think Super-Intelligence Expansion:
1. Open-Source AI Models Engine (DeepSeek-R1, Qwen 2.5 Coder, Llama 3.3, Ollama)
2. Mobile Automation Lane (Android ADB, UIAutomator, Gestures, Calls, SMS, iOS)
3. Enhanced Computer & Desktop Automation (Window focus, keystrokes, clipboard, process control)
4. Telephony & Communication Lane (Cellular calls, SIP, IVR TwiML, Astra Multimodal Voice)
5. Scientific Research Lane (ArXiv papers, literature reviews, LaTeX builder, BibTeX, statistics)
6. Office Productivity Suite (Word .docx, PowerPoint .pptx & HTML, Excel .xlsx formulas & financial modeling)
7. End-to-end Execution & MCP Integration
"""

import sys
import os
import unittest
import asyncio
import tempfile
import zipfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from kosif_think.connectors.open_source_engine import OpenSourceEngine
from kosif_think.lanes.mobile import MobileLane, AndroidController
from kosif_think.lanes.computer.app_control import AppControl
from kosif_think.lanes.telephony import TelephonyLane, CallManager, AstraVoiceSession
from kosif_think.lanes.research import (
    ResearchLane, AcademicSearchEngine, LiteratureReviewSynthesizer,
    LatexBuilder, CitationEngine, StatisticalVerifier
)
from kosif_think.lanes.office import (
    OfficeLane, WordDocumentBuilder, PowerPointBuilder, ExcelEngine
)
from kosif_think.core.executor import ThinkExecutor
from kosif_think.core.planner import TaskPlanner, Step, Target
from kosif_think.server.mcp import handle_tool_call


class TestOpenSourceModelsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OpenSourceEngine()

    def test_catalog_and_model_specs(self):
        models = self.engine.list_models()
        self.assertGreaterEqual(len(models), 6)
        ids = [m["model_id"] for m in models]
        self.assertIn("deepseek-r1", ids)
        self.assertIn("qwen-2.5-coder-32b", ids)
        self.assertIn("llama-3.3-70b", ids)

    def test_optimal_model_selection(self):
        self.assertEqual(self.engine.select_best_model("complex mathematical proof"), "deepseek-r1")
        self.assertEqual(self.engine.select_best_model("write python ast patcher"), "qwen-2.5-coder-32b")
        self.assertEqual(self.engine.select_best_model("screen gui element click"), "ui-tars-7b")
        self.assertEqual(self.engine.select_best_model("fast quick summary"), "phi-4")

    def test_deepseek_r1_reasoning_synthesis(self):
        res = self.engine.run_inference(
            prompt="Prove that the square root of 2 is irrational",
            model_id="deepseek-r1"
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("DeepSeek-R1", res["response"])
        self.assertIn("think_buffer", res)
        self.assertGreater(len(res["think_buffer"]), 20)

    def test_qwen_coder_synthesis(self):
        res = self.engine.run_inference(
            prompt="Implement binary search in Python",
            model_id="qwen-2.5-coder-32b"
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("Qwen", res["response"])


class TestMobileLane(unittest.TestCase):
    def setUp(self):
        self.android = AndroidController()
        self.lane = MobileLane()

    def test_android_controller_actions(self):
        # Tap
        tap_res = self.android.tap(500, 800)
        self.assertEqual(tap_res["action"], "tap")
        self.assertEqual(tap_res["x"], 500)

        # Swipe
        swipe_res = self.android.swipe(100, 200, 100, 800)
        self.assertEqual(swipe_res["action"], "swipe")

        # Key press
        key_res = self.android.press_key("KEYCODE_BACK")
        self.assertEqual(key_res["keycode"], "KEYCODE_BACK")

        # Telephony & SMS
        call_res = self.android.dial_call("+18005550199")
        self.assertEqual(call_res["action"], "dial_call")
        self.assertEqual(call_res["number"], "+18005550199")

        sms_res = self.android.send_sms("+18005550199", "Meeting scheduled")
        self.assertEqual(sms_res["action"], "send_sms")
        self.assertEqual(sms_res["body"], "Meeting scheduled")

    def test_android_ui_dump_and_bounds_parser(self):
        xml_sample = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
        <hierarchy rotation="0">
            <node text="Settings" resource-id="com.android.settings:id/title" bounds="[100,200][300,280]" />
            <node text="Confirm Payment" resource-id="com.app:id/btn_pay" bounds="[200,800][800,900]" />
        </hierarchy>"""
        bounds = self.android._parse_bounds_from_xml(xml_sample, "Confirm Payment")
        self.assertIsNotNone(bounds)
        self.assertEqual(bounds[0], 500)  # center x
        self.assertEqual(bounds[1], 850)  # center y

    def test_mobile_lane_dispatch_step(self):
        step = Step(step_id=1, lane="mobile", intent="launch_app", value="WhatsApp")
        res = asyncio.run(self.lane.dispatch_step(step))
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["lane"], "mobile")


class TestComputerAppControl(unittest.TestCase):
    def setUp(self):
        self.apps = AppControl()

    def test_list_running_apps(self):
        apps = self.apps.list_running_apps()
        self.assertIsInstance(apps, list)
        self.assertGreater(len(apps), 0)

    def test_clipboard_operations(self):
        test_txt = "KOSIF-THINK-TEST-CLIPBOARD-123"
        ok = self.apps.set_clipboard_text(test_txt)
        if ok:
            val = self.apps.get_clipboard_text()
            self.assertEqual(val, test_txt)


class TestTelephonyLane(unittest.TestCase):
    def setUp(self):
        self.lane = TelephonyLane()
        self.mgr = CallManager()

    def test_call_dial_and_hangup(self):
        dial = self.mgr.dial_phone("+966500000000", provider="cellular")
        self.assertEqual(dial["status"], "dialing")
        self.assertIn("call_id", dial)

        hangup = self.mgr.hangup_call(dial["call_id"])
        self.assertEqual(hangup["status"], "terminated")

    def test_virtual_meeting_link_generation(self):
        meet = self.mgr.create_meeting_link("google_meet", "Q3 Strategic Alignment")
        self.assertIn("meet.google.com", meet["meeting_url"])

        zoom = self.mgr.create_meeting_link("zoom", "Board of Directors")
        self.assertIn("zoom.us", zoom["meeting_url"])

    def test_twiml_generation(self):
        twiml = self.mgr.generate_twiml_response("مرحباً بكم في نظام كوسف للذكاء الاصطناعي")
        self.assertIn("<Say", twiml)
        self.assertIn("Polly.Zeina", twiml)

    def test_astra_multimodal_voice_session(self):
        session = AstraVoiceSession()
        init = session.start_session("أهلاً بك، تفضل بالسؤال")
        self.assertEqual(init["state"], "listening")

        # Process user utterance
        res = session.process_user_speech(transcribed_text="ما هي أفضل استراتيجية لتوزيع الخوادم؟")
        self.assertEqual(res["current_state"], "listening")
        self.assertIn("assistant_reply", res)
        self.assertIn("think_trace", res)

        # Barge-in interruption
        inter = session.interrupt()
        self.assertEqual(inter["current_state"], "listening")


class TestScientificResearchLane(unittest.TestCase):
    def setUp(self):
        self.lane = ResearchLane()
        self.search = AcademicSearchEngine()
        self.review = LiteratureReviewSynthesizer()
        self.latex = LatexBuilder()
        self.citations = CitationEngine()
        self.stats = StatisticalVerifier()

    def test_academic_search_local_corpus(self):
        results = self.search.search_local_corpus("DeepSeek Reasoning RL", max_results=3)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("DeepSeek", results[0]["title"])

    def test_literature_review_synthesis(self):
        papers = self.search.search_local_corpus("Transformer Attention", max_results=3)
        rev = self.review.synthesize_review("Foundational Transformer Architectures", papers)
        self.assertIn("executive_summary", rev)
        self.assertIn("benchmark_matrix", rev)
        self.assertIn("research_gaps", rev)
        self.assertIn("markdown_review", rev)

    def test_latex_document_generation(self):
        latex = self.latex.generate_paper_latex(
            title="Scalable Bayesian Agent Networks",
            authors=["Dr. Kosif", "AI Research Lab"],
            abstract="This paper introduces a continuous Bayesian belief propagation framework.",
            sections=[
                {"title": "Introduction", "content": "Autonomous agents require formal verification."},
                {"title": "Methodology", "content": "We define a directed acyclic task graph."}
            ],
            equations=["P(H|E) = \\frac{P(E|H)P(H)}{P(E)}"]
        )
        self.assertIn("\\documentclass", latex)
        self.assertIn("\\begin{document}", latex)
        self.assertIn("Bayesian", latex)
        self.assertIn("\\end{document}", latex)

    def test_citations_formatting(self):
        paper = {
            "title": "DeepSeek-R1 Technical Report",
            "authors": ["Daya Guo", "Dejian Yang"],
            "year": 2025,
            "paper_id": "2501.12948",
            "doi": "10.48550/arXiv.2501.12948"
        }
        bib = self.citations.to_bibtex(paper)
        self.assertIn("@article{", bib)
        self.assertIn("DeepSeek-R1", bib)

        apa = self.citations.to_apa(paper)
        self.assertIn("(2025)", apa)

    def test_statistical_rigor_verification(self):
        group_a = [85.0, 87.0, 88.5, 86.2, 89.1, 87.4]
        group_b = [78.0, 79.2, 77.5, 80.1, 78.4, 79.0]
        res = self.stats.two_sample_t_test(group_a, group_b)
        self.assertGreater(res["mean_a"], res["mean_b"])
        self.assertTrue(res["is_significant_p05"])
        self.assertEqual(res["effect_size_magnitude"], "large")


class TestOfficeProductivityLane(unittest.TestCase):
    def setUp(self):
        self.lane = OfficeLane()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_word_document_creation(self):
        doc = WordDocumentBuilder(title="Quarterly Intelligence Assessment")
        doc.add_heading("Strategic AI Infrastructure", level=1)
        doc.add_paragraph("KOSIF Think provides unified multi-device automation.", bold=True)
        doc.add_bullet_point("Android ADB & UIAutomator integration")
        doc.add_bullet_point("Deep-Think Long-CoT test-time compute")
        doc.add_callout("All data models are verified by symbolic truth contracts.", title="VERIFIED")
        doc.add_table(
            headers=["Lane", "Throughput", "Security"],
            rows=[
                ["Mobile", "120 ops/sec", "Isolated ADB"],
                ["Office", "Instant XML", "Native Zip"]
            ]
        )
        out_path = os.path.join(self.temp_dir.name, "test_doc.docx")
        saved = doc.save(out_path)
        self.assertTrue(os.path.exists(saved))
        self.assertTrue(zipfile.is_zipfile(saved))

        # Check OpenXML internal files
        with zipfile.ZipFile(saved, 'r') as z:
            names = z.namelist()
            self.assertIn("[Content_Types].xml", names)
            self.assertIn("word/document.xml", names)

    def test_powerpoint_presentation_creation(self):
        ppt = PowerPointBuilder(title="Super-Intelligence Roadmap", theme="dark")
        ppt.add_title_slide("Super-Intelligence Architecture", "12 Autonomous Lanes", "KOSIF Team")
        ppt.add_content_slide("Key Pillars", ["Multi-Device Control", "Long-CoT Deep Deliberation", "Native Office Suite"])
        ppt.add_comparison_slide("Ecosystem Comparison", "Standard LLMs", ["Cloud only", "No ADB"], "KOSIF Think", ["Android+iOS", "Full Office"])
        ppt.add_metrics_slide("Empirical Results", [{"value": "97.3%", "label": "Accuracy"}, {"value": "12", "label": "Lanes"}])

        out_path = os.path.join(self.temp_dir.name, "presentation.pptx")
        saved = ppt.save(out_path)
        self.assertTrue(os.path.exists(saved))
        self.assertTrue(zipfile.is_zipfile(saved))

        # Check HTML presentation viewer export
        html_viewer = ppt.export_html_viewer()
        self.assertIn("deck-card", html_viewer)
        self.assertIn("Slide 1 /", html_viewer)

    def test_excel_spreadsheet_and_financial_model(self):
        excel = ExcelEngine()

        # Formula evaluation
        self.assertEqual(excel.evaluate_formula("=SUM(10, 20, 30, 40)"), 100.0)
        self.assertEqual(excel.evaluate_formula("=AVERAGE(10, 20, 30)"), 20.0)
        self.assertEqual(excel.evaluate_formula('=IF(5 > 3, "Yes", "No")'), "Yes")

        # Financial Model
        model = excel.generate_financial_model(base_revenue=500000.0, growth_rate=0.20, years=3)
        self.assertEqual(len(model["revenue"]), 3)
        self.assertGreater(model["revenue"][2], model["revenue"][0])

        # Data Profiler
        profile = excel.profile_data([10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertEqual(profile["mean"], 30.0)
        self.assertEqual(profile["min"], 10.0)
        self.assertEqual(profile["max"], 50.0)

        # Save XLSX
        out_xlsx = os.path.join(self.temp_dir.name, "model.xlsx")
        saved_xlsx = excel.save_xlsx(out_xlsx)
        self.assertTrue(os.path.exists(saved_xlsx))
        self.assertTrue(zipfile.is_zipfile(saved_xlsx))

        # Save CSV
        out_csv = os.path.join(self.temp_dir.name, "model.csv")
        saved_csv = excel.save_csv(out_csv, sheet_name="Financial_Model")
        self.assertTrue(os.path.exists(saved_csv))


class TestMCPToolsAndPlanningIntegration(unittest.TestCase):
    def test_planner_intent_classification(self):
        planner = TaskPlanner()

        # Office Word intent
        p_word = planner.create_plan(type("R", (), {"clean_goal": "انشئ مستند وورد docx للخطة السنوية", "task_id": "1"})())
        self.assertEqual(p_word.steps[0].lane, "office")
        self.assertEqual(p_word.steps[0].intent, "word")

        # Office PPT intent
        p_ppt = planner.create_plan(type("R", (), {"clean_goal": "صمم عرض بوربوينت pptx لنتائج الربع الأول", "task_id": "2"})())
        self.assertEqual(p_ppt.steps[0].lane, "office")
        self.assertEqual(p_ppt.steps[0].intent, "ppt")

        # Scientific research intent
        p_res = planner.create_plan(type("R", (), {"clean_goal": "قم بإجراء بحث علمي في arxiv عن النماذج التوليدية", "task_id": "3"})())
        self.assertEqual(p_res.steps[0].lane, "research")

        # Mobile control intent
        p_mob = planner.create_plan(type("R", (), {"clean_goal": "انقر على زر الشراء في شاشة الجوال", "task_id": "4"})())
        self.assertEqual(p_mob.steps[0].lane, "mobile")

        # Telephony intent
        p_tel = planner.create_plan(type("R", (), {"clean_goal": "اتصل برقم 966500000000", "task_id": "5"})())
        self.assertEqual(p_tel.steps[0].lane, "telephony")

    def test_mcp_new_tool_invocations(self):
        # 1. MCP mobile action
        mob_res = asyncio.run(handle_tool_call("think_mobile_action", {"intent": "tap", "value": "400,600"}))
        self.assertEqual(mob_res["status"], "ok")

        # 2. MCP telephony call
        call_res = asyncio.run(handle_tool_call("think_telephony_call", {"intent": "dial", "target": "+18005550199"}))
        self.assertEqual(call_res["status"], "dialing")

        # 3. MCP scientific research
        res_res = asyncio.run(handle_tool_call("think_scientific_research", {"intent": "search", "target": "DeepSeek"}))
        self.assertEqual(res_res["status"], "ok")

        # 4. MCP office generate
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            tmp_name = f.name
        try:
            off_res = asyncio.run(handle_tool_call("think_office_generate", {"intent": "excel", "filename": tmp_name}))
            self.assertEqual(off_res["status"], "ok")
            self.assertTrue(os.path.exists(tmp_name))
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

        # 5. MCP open models inference
        om_res = asyncio.run(handle_tool_call("think_open_models_inference", {"prompt": "What is 2+2?", "model": "deepseek-r1"}))
        self.assertEqual(om_res["status"], "success")


if __name__ == "__main__":
    unittest.main()
