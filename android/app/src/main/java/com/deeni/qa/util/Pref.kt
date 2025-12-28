package com.deeni.qa.util

import android.content.Context

object Pref {
    private const val NAME = "deeniqa_prefs"
    private const val KEY_BASE_URL = "base_url"
    private const val DEFAULT_BASE_URL = "http://10.0.2.2:8000/" // Emulator to host

    fun getBaseUrl(ctx: Context): String {
        val sp = ctx.getSharedPreferences(NAME, Context.MODE_PRIVATE)
        return sp.getString(KEY_BASE_URL, DEFAULT_BASE_URL) ?: DEFAULT_BASE_URL
    }

    fun setBaseUrl(ctx: Context, url: String) {
        val sp = ctx.getSharedPreferences(NAME, Context.MODE_PRIVATE)
        sp.edit().putString(KEY_BASE_URL, url).apply()
    }
}
