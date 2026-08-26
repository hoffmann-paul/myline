//
//  Settings.swift
//  MyLine Mobile
//
//  Created by Paul Hoffmann on 26.08.26.
//

import SwiftUI

struct SettingsView: View {
    
    func import_data() {
        
    }
    
    func export_data() {
        
    }
    
    var body: some View {
        VStack() {
            Button("Import Data") {
                import_data()
            }
            .frame(width: 200, height: 50)
            .background(Color.accentColor)
            .cornerRadius(10)
            .foregroundStyle(Color.black)
            
            Button("Export Data") {
                export_data()
            }
            .frame(width: 200, height: 50)
            .background(Color.accentColor)
            .cornerRadius(10)
            .foregroundStyle(Color.black)
            
            
            Spacer()
        }
    }
}

#Preview {
    Settings()
}
