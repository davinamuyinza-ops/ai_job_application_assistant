import { getAccessToken } from "./auth.js";
import { API_BASE_URL } from "./config.js";

export async function apiFetch(path, options = {}) {
    const token = await getAccessToken();

    const isFormData = options.body instanceof FormData;

    const headers = {
        ...(options.body && !isFormData ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    return fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });
}

export async function apiJson(path, options = {}) {
    const response = await apiFetch(path, options);

    if (!response.ok) {
        let detail;

        try {
            detail = await response.json();
        } catch {
            detail = { error: response.statusText };
        }

        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    return response.json();
}
