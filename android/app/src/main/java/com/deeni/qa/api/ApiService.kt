package com.deeni.qa.api

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("ask")
    fun ask(@Body body: AskRequest): Call<AskResponse>
}
