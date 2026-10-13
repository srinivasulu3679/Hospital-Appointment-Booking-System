from pathlib import Path

from app.services.prescription_pdf_service import generate_prescription_pdf


def test_generate_prescription_pdf():
    pdf_path = generate_prescription_pdf(
        prescription_id=1,
        patient_name="Test Patient",
        doctor_name="Test Doctor",
        medicines="Medicine A",
        instructions="Take as directed",
    )

    assert pdf_path is not None
    assert Path(pdf_path).exists()
    assert Path(pdf_path).stat().st_size > 0
