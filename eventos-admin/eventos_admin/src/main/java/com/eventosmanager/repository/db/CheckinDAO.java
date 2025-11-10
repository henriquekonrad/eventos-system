package com.eventosmanager.repository.db;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

import com.eventosmanager.config.DatabaseConfig;
import com.eventosmanager.models.Checkin;

/**
 * DAO (Data Access Object) para Check-ins offline.
 * Gerencia persistência no SQLite local.
 */
public class CheckinDAO {
    
    private final DatabaseConfig dbConfig;
    private static final DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
    
    public CheckinDAO() {
        this.dbConfig = DatabaseConfig.getInstance();
    }
    
    /**
     * Salva um check-in no banco offline
     */
    public boolean salvar(Checkin checkin) {
        String sql =
        "INSERT INTO checkins_offline " +
        "(inscricao_id, ingresso_id, usuario_id, evento_id, ocorrido_em, sincronizado) " +
        "VALUES (?, ?, ?, ?, ?, 0);";
        
        try (Connection conn = dbConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, checkin.getInscricaoId());
            pstmt.setString(2, checkin.getIngressoId());
            pstmt.setString(3, checkin.getUsuarioId());
            pstmt.setString(4, checkin.getEventoId());
            pstmt.setString(5, checkin.getOcorridoEm().format(formatter));
            
            int rowsAffected = pstmt.executeUpdate();
            
            if (rowsAffected > 0) {
                System.out.println("✅ Check-in salvo offline: " + checkin.getInscricaoId());
                return true;
            }
            return false;
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao salvar check-in offline: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * Busca todos os check-ins pendentes de sincronização
     */
    public List<Checkin> buscarPendentes() {
        List<Checkin> checkins = new ArrayList<>();
        String sql = "SELECT * FROM checkins_offline WHERE sincronizado = 0";
        
        try (Connection conn = dbConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Checkin checkin = new Checkin();
                checkin.setId(rs.getInt("id"));
                checkin.setInscricaoId(rs.getString("inscricao_id"));
                checkin.setIngressoId(rs.getString("ingresso_id"));
                checkin.setUsuarioId(rs.getString("usuario_id"));
                checkin.setEventoId(rs.getString("evento_id"));
                checkin.setOcorridoEm(LocalDateTime.parse(rs.getString("ocorrido_em"), formatter));
                checkin.setSincronizado(rs.getInt("sincronizado") == 1);
                
                checkins.add(checkin);
            }
            
            System.out.println("📋 Encontrados " + checkins.size() + " check-ins pendentes.");
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao buscar check-ins pendentes: " + e.getMessage());
        }
        
        return checkins;
    }
    
    /**
     * Marca um check-in como sincronizado
     */
    public boolean marcarComoSincronizado(int id) {
        String sql = "UPDATE checkins_offline SET sincronizado = 1 WHERE id = ?";
        
        try (Connection conn = dbConfig.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, id);
            int rowsAffected = pstmt.executeUpdate();
            
            if (rowsAffected > 0) {
                System.out.println("✅ Check-in ID " + id + " marcado como sincronizado.");
                return true;
            }
            return false;
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao marcar como sincronizado: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Conta quantos check-ins estão pendentes de sincronização
     */
    public int contarPendentes() {
        String sql = "SELECT COUNT(*) as total FROM checkins_offline WHERE sincronizado = 0";
        
        try (Connection conn = dbConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            if (rs.next()) {
                return rs.getInt("total");
            }
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao contar pendentes: " + e.getMessage());
        }
        
        return 0;
    }
    
    /**
     * Remove todos os check-ins já sincronizados
     */
    public void limparSincronizados() {
        String sql = "DELETE FROM checkins_offline WHERE sincronizado = 1";
        
        try (Connection conn = dbConfig.getConnection();
             Statement stmt = conn.createStatement()) {
            
            int deleted = stmt.executeUpdate(sql);
            System.out.println("🧹 " + deleted + " check-ins sincronizados removidos.");
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao limpar sincronizados: " + e.getMessage());
        }
    }
    
    /**
     * Busca todos os check-ins (para debug/visualização)
     */
    public List<Checkin> buscarTodos() {
        List<Checkin> checkins = new ArrayList<>();
        String sql = "SELECT * FROM checkins_offline ORDER BY criado_em DESC";
        
        try (Connection conn = dbConfig.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Checkin checkin = new Checkin();
                checkin.setId(rs.getInt("id"));
                checkin.setInscricaoId(rs.getString("inscricao_id"));
                checkin.setIngressoId(rs.getString("ingresso_id"));
                checkin.setUsuarioId(rs.getString("usuario_id"));
                checkin.setEventoId(rs.getString("evento_id"));
                checkin.setOcorridoEm(LocalDateTime.parse(rs.getString("ocorrido_em"), formatter));
                checkin.setSincronizado(rs.getInt("sincronizado") == 1);
                
                checkins.add(checkin);
            }
            
        } catch (SQLException e) {
            System.err.println("❌ Erro ao buscar todos: " + e.getMessage());
        }
        
        return checkins;
    }
}