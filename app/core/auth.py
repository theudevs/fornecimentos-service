import uuid
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

try:
    import jwt
except ModuleNotFoundError:
    jwt = None  # type: ignore[assignment]


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    empresa_id: uuid.UUID
    roles: list[str]
    user_id: str | None = None
    email: str | None = None
    name: str | None = None
    source: str = "jwt"


def _normalize_roles(raw_roles: Any) -> list[str]:
    if raw_roles is None:
        return []
    if isinstance(raw_roles, str):
        return [raw_roles.upper()]
    if isinstance(raw_roles, list):
        return [str(role).upper() for role in raw_roles]
    return []


def _decode_token(token: str, settings: Settings) -> dict[str, Any]:
    if jwt is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PyJWT nao instalado. Rode pip install -r requirements.txt.",
        )

    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET nao configurado no servico de fornecimentos.",
        )

    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            leeway=settings.jwt_clock_skew_seconds,
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.") from exc


def _context_from_claims(claims: dict[str, Any]) -> AuthContext:
    empresa_claim = claims.get("empresa_id")
    if not empresa_claim:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem empresa_id.")

    try:
        empresa_id = uuid.UUID(str(empresa_claim))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="empresa_id do token invalido.") from exc

    roles = _normalize_roles(claims.get("role") or claims.get("roles") or claims.get("perfil") or claims.get("perfis"))
    if roles and "FORNECEDOR" not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token nao possui perfil FORNECEDOR.")

    return AuthContext(
        empresa_id=empresa_id,
        roles=roles,
        user_id=str(claims.get("sub")) if claims.get("sub") else None,
        email=str(claims.get("email")) if claims.get("email") else None,
        name=str(claims.get("name")) if claims.get("name") else None,
    )


def get_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    x_empresa_id: Annotated[
        uuid.UUID | None,
        Header(
            alias="X-Empresa-Id",
            description="Fallback local quando AUTH_ENABLED=false. Em integracao, use Authorization: Bearer <JWT>.",
        ),
    ] = None,
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    if credentials:
        claims = _decode_token(credentials.credentials, settings)
        return _context_from_claims(claims)

    if settings.auth_enabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Bearer obrigatorio.")

    if x_empresa_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Informe Authorization Bearer ou X-Empresa-Id para teste local.",
        )

    return AuthContext(empresa_id=x_empresa_id, roles=["FORNECEDOR"], source="header")
