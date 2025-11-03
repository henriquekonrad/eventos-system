package com.eventosmanager.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class AppConfig {
    private static Properties props = new Properties();

    static {
        try (InputStream input = AppConfig.class.getClassLoader().getResourceAsStream("application.properties")) {
            if (input != null) {
                props.load(input);
            } else {
                throw new RuntimeException("application.properties não encontrado");
            }
        } catch (IOException e) {
            throw new RuntimeException("Erro ao carregar configuração", e);
        }
    }

    public static String get(String key) {
        return props.getProperty(key);
    }
}
