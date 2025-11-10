package com.eventosmanager.config;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * 🎯 SINGLETON PATTERN
 * Gerencia a conexão única com o banco SQLite local (offline).
 * Cria as tabelas automaticamente na primeira conexão.
 */
public class DatabaseConfig {
    
    private static DatabaseConfig instance;
    private Connection connection;
    private static final String DB_URL = "jdbc:sqlite:eventos_offline.db";
    
    /**
     * Construtor privado (Singleton)
     */
    private DatabaseConfig() {
        try {
            // Carrega o driver SQLite
            Class.forName("org.sqlite.JDBC");
            
            // Cria conexão
            connection = DriverManager.getConnection(DB_URL);
            
            System.out.println("✅ Conexão com SQLite estabelecida!");
            
            // Cria tabelas se não existirem
            createTables();
            
        } catch (ClassNotFoundException e) {
            System.err.println("❌ Driver SQLite não encontrado!");
            System.err.println("   Adicione no pom.xml: org.xerial:sqlite-jdbc");
            throw new RuntimeException("Driver SQLite não encontrado", e);
        } catch (SQLException e) {
            System.err.println("❌ Erro ao conectar no SQLite: " + e.getMessage());
            throw new RuntimeException("Erro ao conectar no SQLite", e);
        }
    }
    
    /**
     * Retorna a instância única (Singleton)
     */
    public static synchronized DatabaseConfig getInstance() {
        if (instance == null) {
            instance = new DatabaseConfig();
        }
        return instance;
    }
    
    /**
     * Retorna a conexão ativa
     */
    public Connection getConnection() {
        try {
            // Verifica se a conexão está fechada e reconecta se necessário
            if (connection == null || connection.isClosed()) {
                connection = DriverManager.getConnection(DB_URL);
            }
        } catch (SQLException e) {
            System.err.println("❌ Erro ao verificar/reconectar: " + e.getMessage());
        }
        return connection;
    }
    
    /**
     * Cria as tabelas necessárias para operação offline
     */
    private void createTables() {
        try (Statement stmt = connection.createStatement()) {
            
            // Tabela de check-ins offline
            String createCheckinsTable =
            "CREATE TABLE IF NOT EXISTS checkins_offline (\n" +
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n" +
            "    inscricao_id TEXT NOT NULL,\n" +
            "    ingresso_id TEXT NOT NULL,\n" +
            "    usuario_id TEXT NOT NULL,\n" +
            "    evento_id TEXT NOT NULL,\n" +
            "    ocorrido_em TEXT NOT NULL,\n" +
            "    sincronizado INTEGER DEFAULT 0,\n" +
            "    criado_em TEXT DEFAULT CURRENT_TIMESTAMP\n" +
            ");";
            stmt.execute(createCheckinsTable);
            
            // Tabela de inscrições rápidas offline
            String createInscricoesTable =
            "CREATE TABLE IF NOT EXISTS inscricoes_rapidas_offline (\n" +
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n" +
            "    evento_id TEXT NOT NULL,\n" +
            "    nome TEXT NOT NULL,\n" +
            "    cpf TEXT NOT NULL,\n" +
            "    email TEXT NOT NULL,\n" +
            "    sincronizado INTEGER DEFAULT 0,\n" +
            "    criado_em TEXT DEFAULT CURRENT_TIMESTAMP\n" +
            ");";
            stmt.execute(createInscricoesTable);
            
            // Índices para performance
            stmt.execute("CREATE INDEX IF NOT EXISTS idx_checkins_sync ON checkins_offline(sincronizado)");
            stmt.execute("CREATE INDEX IF NOT EXISTS idx_inscricoes_sync ON inscricoes_rapidas_offline(sincronizado)");
            
            System.out.println("✅ Tabelas SQLite criadas/verificadas com sucesso!");
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao criar tabelas: " + e.getMessage());
            throw new RuntimeException("Erro ao criar tabelas", e);
        }
    }
    
    /**
     * Fecha a conexão com o banco
     */
    public void close() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
                System.out.println("🔌 Conexão SQLite fechada.");
            }
        } catch (SQLException e) {
            System.err.println("⚠️ Erro ao fechar conexão: " + e.getMessage());
        }
    }
    
    /**
     * Limpa todos os dados sincronizados (usado após sincronização)
     */
    public void limparDadosSincronizados() {
        try (Statement stmt = connection.createStatement()) {
            stmt.execute("DELETE FROM checkins_offline WHERE sincronizado = 1");
            stmt.execute("DELETE FROM inscricoes_rapidas_offline WHERE sincronizado = 1");
            System.out.println("🧹 Dados sincronizados limpos do SQLite.");
        } catch (SQLException e) {
            System.err.println("⚠️ Erro ao limpar dados: " + e.getMessage());
        }
    }
}