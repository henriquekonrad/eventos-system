package com.eventosmanager.api.api_utils;

import com.google.gson.Gson;
import java.util.Base64;
import java.util.Map;

public class JwtUtils {
    public static Map<String, Object> decode(String jwtToken) {
        try {
            String[] parts = jwtToken.split("\\.");
            String payloadJson = new String(Base64.getUrlDecoder().decode(parts[1]));
            return new Gson().fromJson(payloadJson, Map.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao decodificar JWT", e);
        }
    }
}
