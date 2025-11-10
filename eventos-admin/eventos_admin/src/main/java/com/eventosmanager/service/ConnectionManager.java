package com.eventosmanager.service;

public class ConnectionManager {
    private static boolean forceOffline = false; // 🔘 SIMULA OFFLINE
    
    public static boolean isOnline() {
        if (forceOffline) return false; // simula offline
        else return true;
    }
    
    public static void setForceOffline(boolean offline) {
        forceOffline = offline;
    }
}
