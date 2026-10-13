import os
from uuid import uuid4
from html import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


UPLOAD_DIR = "uploads/prescriptions"


def generate_prescription_pdf(
    prescription=None,
    prescription_id=None,
    patient_name="Not specified",
    doctor_name="Not specified",
    medicines="Not specified",
    instructions="No additional instructions",
) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"prescription_{uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)

    if prescription is not None:
        prescription_id = getattr(prescription, "id", prescription_id)
        consultation_id = getattr(prescription, "consultation_id", None)
        doctor_id = getattr(prescription, "doctor_id", None)
        patient_id = getattr(prescription, "patient_id", None)
        medicines = getattr(prescription, "medicines", medicines)
        instructions = getattr(prescription, "instructions", instructions)
    else:
        consultation_id = None
        doctor_id = None
        patient_id = None

    styles = getSampleStyleSheet()
    story = [
        Paragraph("Hospital Prescription", styles["Title"]),
        Spacer(1, 0.3 * inch),
        Paragraph(
            f"Prescription ID: {escape(str(prescription_id or 'Not specified'))}",
            styles["Normal"],
        ),
        Paragraph(
            f"Patient: {escape(str(patient_name or 'Not specified'))}",
            styles["Normal"],
        ),
        Paragraph(
            f"Doctor: {escape(str(doctor_name or 'Not specified'))}",
            styles["Normal"],
        ),
    ]

    if consultation_id is not None:
        story.append(
            Paragraph(
                f"Consultation ID: {escape(str(consultation_id))}",
                styles["Normal"],
            )
        )

    if doctor_id is not None:
        story.append(
            Paragraph(f"Doctor ID: {escape(str(doctor_id))}", styles["Normal"])
        )

    if patient_id is not None:
        story.append(
            Paragraph(f"Patient ID: {escape(str(patient_id))}", styles["Normal"])
        )

    story.extend([
        Spacer(1, 0.2 * inch),
        Paragraph("Medicines", styles["Heading2"]),
        Paragraph(escape(str(medicines or "Not specified")), styles["Normal"]),
        Spacer(1, 0.2 * inch),
        Paragraph("Instructions", styles["Heading2"]),
        Paragraph(
            escape(str(instructions or "No additional instructions")),
            styles["Normal"],
        ),
    ])

    document = SimpleDocTemplate(file_path, pagesize=A4)
    document.build(story)

    return file_path