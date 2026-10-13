
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserRoleUpdate,
)
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
)
from app.schemas.doctor_schedule import (
    DoctorScheduleCreate,
    DoctorScheduleResponse,
)
from app.schemas.doctor_leave import (
    DoctorLeaveCreate,
    DoctorLeaveResponse,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentStatusUpdate,
    AppointmentReschedule,
    AppointmentResponse,
)
from app.schemas.appointment_history import (
    AppointmentHistoryCreate,
    AppointmentHistoryResponse,
)
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationResponse,
)
from app.schemas.consultation_file import ConsultationFileResponse
from app.schemas.refresh_token import (
    RefreshTokenRequest,
    RefreshTokenResponse,
    RefreshTokenInfo,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationReadUpdate,
)
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse
from app.schemas.doctor_rating import DoctorRatingCreate, DoctorRatingResponse
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
)
from app.schemas.email_log import EmailLogCreate, EmailLogResponse
from app.schemas.appointment_reminder import (
    AppointmentReminderCreate,
    AppointmentReminderResponse,
)
from app.schemas.doctor_queue import (
    DoctorQueueCreate,
    DoctorQueueStatusUpdate,
    DoctorQueueResponse,
)
from app.schemas.doctor_availability import (
    DoctorAvailabilityCreate,
    DoctorAvailabilityUpdate,
    DoctorAvailabilityResponse,
)
