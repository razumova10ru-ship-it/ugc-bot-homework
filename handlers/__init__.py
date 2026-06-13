from .start import router as start_router
from .navigation import router as navigation_router
from .form import router as form_router
from .education import router as education_router
from .manager import router as manager_router
from .fallback import router as fallback_router
from .menu import router as menu_router
from .onboarding import router as onboarding_router
from .utm import router as utm_router
from .notifications import router as notifications_router, setup_scheduler

__all__ = [
    "start_router",
    "navigation_router",
    "form_router",
    "education_router",
    "manager_router",
    "fallback_router",
    "menu_router",
    "onboarding_router",
    "utm_router",
    "notifications_router",
    "setup_scheduler",
]
