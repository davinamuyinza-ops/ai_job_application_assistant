import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { SUPABASE_ANON_KEY, SUPABASE_URL } from "./config.js";
import { state } from "./state.js";

const isConfigured =
    SUPABASE_URL.startsWith("http") &&
    Boolean(SUPABASE_ANON_KEY) &&
    SUPABASE_ANON_KEY !== "REPLACE_WITH_SUPABASE_ANON_KEY";

export const supabase = isConfigured ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY) : null;

export function isSupabaseConfigured() {
    return isConfigured;
}

function requireSupabase() {
    if (!supabase) {
        throw new Error(
            "Supabase is not configured yet - set SUPABASE_URL and SUPABASE_ANON_KEY in frontend/js/config.js.",
        );
    }
}

export async function signUp(email, password) {
    requireSupabase();

    const { data, error } = await supabase.auth.signUp({ email, password });

    if (error) {
        throw error;
    }

    return data;
}

export async function signIn(email, password) {
    requireSupabase();

    const { data, error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
        throw error;
    }

    state.session = data.session;

    return data;
}

export async function signOut() {
    if (!supabase) {
        return;
    }

    await supabase.auth.signOut();
    state.session = null;
}

export async function getSession() {
    if (!supabase) {
        return null;
    }

    const { data } = await supabase.auth.getSession();
    state.session = data.session;
    return data.session;
}

export function onAuthStateChange(callback) {
    if (!supabase) {
        return;
    }

    supabase.auth.onAuthStateChange((_event, session) => {
        state.session = session;
        callback(session);
    });
}

export async function getAccessToken() {
    if (!supabase) {
        return null;
    }

    if (!state.session) {
        await getSession();
    }

    return state.session ? state.session.access_token : null;
}
