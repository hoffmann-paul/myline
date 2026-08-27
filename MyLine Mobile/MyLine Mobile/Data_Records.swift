//
//  Data_Records.swift
//  MyLine Mobile
//
//  Created by Paul Hoffmann on 26.08.26.
//

import SwiftUI

struct Data_Records: View {
    
    @AppStorage("datasets") private var datasets_string: String = ""
        
    private var datasets: [DataSet] {
        guard let data = datasets_string.data(using: .utf8) else {
            return []
        }
        do {
            return try JSONDecoder().decode([DataSet].self, from: data)
        } catch {
            return []
        }
    }
    
    var body: some View {
        NavigationStack() {
            VStack() {
                HStack() {
                    Spacer()
                    NavigationLink(destination: newDataSet()) {
                        ZStack() {
                            Circle()
                                .fill(.blue)
                                .opacity(0.5)
                            
                            Image(systemName: "plus")
                                .colorScheme(.dark)
                                .bold()
                        }
                        .frame(width: 50, height: 50)
                    }
                }
                
                Spacer()
            }
        }
    }
}

#Preview {
    Data_Records()
}
