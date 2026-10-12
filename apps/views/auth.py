from fastapi import APIRouter, BackgroundTasks, HTTPException

from apps.forms import LoginForm, RefreshTokenRequest, RegisterForm, Token, VerifyOTPForm
from apps.models import SessionDep, User
from apps.utils import (
    check_otp,
    create_access_and_refresh_tokens,
    generate_otp,
    save_otp,
    send_otp_email,
    verify_token,
)

router = APIRouter(tags=["auth"])


@router.post("/user/register")
async def register(register_form: RegisterForm, session: SessionDep, background_tasks: BackgroundTasks):
    instance = User(**register_form.model_dump())
    session.add(instance)
    session.commit()
    session.refresh(instance)

    code = generate_otp()
    save_otp(instance.email, code)
    background_tasks.add_task(send_otp_email, instance.email, code)
    return {"message": "Success create! Kod emailga yuborildi", "status": 201}


@router.post("/user/verify-otp")
async def verify_otp(form: VerifyOTPForm):
    if not check_otp(form.email, form.code):
        raise HTTPException(status_code=400, detail="Kod xato yoki muddati tugagan")
    return {"message": "Kod to'g'ri", "status": 200}


@router.post("/user/login", response_model=Token)
async def login(login_form: LoginForm):
    access, refresh = create_access_and_refresh_tokens(login_form.username)
    return Token(access_token=access, token_type="bearer", refresh_token=refresh)


@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: RefreshTokenRequest):
    username = verify_token(request.refresh_token, token_type="refresh")
    access_token, refresh_token = create_access_and_refresh_tokens(username)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
