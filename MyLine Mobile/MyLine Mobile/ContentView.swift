//
//  ContentView.swift
//  MyLine Mobile
//
//  Created by Paul Hoffmann on 26.08.26.
//

import SwiftUI

struct ContentView: View {
    
    @State private var selection = 0
    
    var body: some View {
        VStack(alignment: .center) {
            TabView(selection: $selection){
                Tab("Data Records",systemImage: "menucard", value: 0){
                    Text("Data Records")
                        .font(.headline)
                        .bold()
                    Data_Records()
                }
                Tab("Settings",systemImage: "gear", value: 1){
                    Text("Settings")
                        .font(.headline)
                        .bold()
                   Settings()
                }
            }
        }.frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .padding()
    }
}

#Preview {
    ContentView()
}
