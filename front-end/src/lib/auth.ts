export const AUTH_TOKEN_KEY = "portal_b2b_jwt";
export const AUTH_SESSION_KEY = "portal_b2b_session";

type AuthSession = {
  empresa?: {
    id?: string;
    perfis?: string[];
  };
};

export function getAuthToken() {
  return sessionStorage.getItem(AUTH_TOKEN_KEY);
}

export function getAuthSession(): AuthSession | null {
  const raw = sessionStorage.getItem(AUTH_SESSION_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

function getEmpresaIdFromToken() {
  const token = getAuthToken();
  const payload = token?.split(".")[1];
  if (!payload) return "";

  try {
    const normalizedPayload = payload.replace(/-/g, "+").replace(/_/g, "/");
    const claims = JSON.parse(atob(normalizedPayload)) as { empresa_id?: string };
    return claims.empresa_id?.trim() || "";
  } catch {
    return "";
  }
}

export function getEmpresaIdFromSession() {
  return getAuthSession()?.empresa?.id?.trim() || getEmpresaIdFromToken();
}

export function hasAuthToken() {
  return Boolean(getAuthToken());
}
