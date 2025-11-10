package com.eventosmanager;

import java.util.List;
import java.util.UUID;

import com.eventosmanager.api.AuthApi;
import com.eventosmanager.config.DatabaseConfig;
import com.eventosmanager.models.Checkin;
import com.eventosmanager.repository.db.CheckinDAO;

public class Main {
    public static void main(String[] args) {
        System.out.println("🚀 Iniciando Eventos Manager - Atendente\n");
        
        // 1. Teste de autenticação (já funcionava)
        System.out.println("=== TESTE DE AUTENTICAÇÃO ===");
        String email = "admin@empresa.com";
        String senha = "senha123";
        
        if (AuthApi.login(email, senha)) {
            AuthApi.getProfile();
        }
        
        System.out.println("\n=== TESTE DE BANCO OFFLINE ===");
        
        // 2. Teste do SQLite
        try {
            DatabaseConfig dbConfig = DatabaseConfig.getInstance();
            System.out.println("✅ SQLite inicializado!");
            
            // 3. Teste do DAO
            CheckinDAO dao = new CheckinDAO();
            
            // Criar um check-in de teste
            Checkin checkin = new Checkin(
                UUID.randomUUID().toString(), // inscricao_id
                UUID.randomUUID().toString(), // ingresso_id
                UUID.randomUUID().toString(), // usuario_id
                UUID.randomUUID().toString()  // evento_id
            );
            
            // Salvar no banco
            boolean salvou = dao.salvar(checkin);
            System.out.println("Salvou check-in: " + salvou);
            
            // Buscar pendentes
            List<Checkin> pendentes = dao.buscarPendentes();
            System.out.println("\n📋 Check-ins pendentes de sincronização:");
            for (Checkin c : pendentes) {
                System.out.println("  - " + c);
            }
            
            // Contar pendentes
            int total = dao.contarPendentes();
            System.out.println("\n📊 Total de pendentes: " + total);
            
        } catch (Exception e) {
            System.err.println("❌ Erro ao testar banco: " + e.getMessage());
            e.printStackTrace();
        }
        
        System.out.println("\n✅ Testes concluídos!");
    }
}