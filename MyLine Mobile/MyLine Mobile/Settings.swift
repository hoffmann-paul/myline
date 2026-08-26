//
//  Settings.swift
//  MyLine Mobile
//
//  Created by Paul Hoffmann on 26.08.26.
//

import SwiftUI
import UniformTypeIdentifiers

struct SettingsView: View {
    
    @State private var showImporter: Bool = false
    @State private var data_records: [DataSet] = []
    
    func import_data(from url: URL) {
        guard url.startAccessingSecurityScopedResource() else { return }
        defer { url.stopAccessingSecurityScopedResource() }

        do {
            let data = try Data(contentsOf: url)
            let decoded = try JSONDecoder().decode([DataSet].self, from: data)
            data_records = decoded
        } catch {}
    }
    
    func export_data() {
        
    }
    
    var body: some View {
        VStack() {
            Button("Import Data") {
                showImporter = true
            }
            .frame(width: 200, height: 50)
            .background(Color.accentColor)
            .cornerRadius(10)
            .foregroundStyle(Color.black)
            .fileImporter(
                        isPresented: $showImporter,
                        allowedContentTypes: [.json],
                        allowsMultipleSelection: false
                    ) { result in
                        switch result {
                        case .success(let urls):
                            guard let url = urls.first else { return }
                            import_data(from: url)
                        case .failure(let error):
                            print(error)
                        }
                    }
            
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
    SettingsView()
}
