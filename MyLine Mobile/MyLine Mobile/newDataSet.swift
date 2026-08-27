//
//  newDataSet.swift
//  MyLine Mobile
//
//  Created by Paul Hoffmann on 27.08.26.
//

import SwiftUI

struct newDataSet: View {
    
    @State private var comment: String = ""
    @State private var name: String = ""
    @State private var age: Int = 0
    @State private var gender: String = ""
    @State private var height: String = ""
    
    var body: some View {
        VStack() {
            TextField("Comment", text: $comment)
                .overlay(
                    RoundedRectangle(cornerRadius: 22)
                        .stroke(.primary, lineWidth: 2)
                        .padding(-5)
                        .frame(height: 30)
                )
                .padding()
            
            TextField("Name", text: $name)
                .overlay(
                    RoundedRectangle(cornerRadius: 22)
                        .stroke(.primary, lineWidth: 2)
                        .padding(-5)
                        .frame(height: 30)
                )
                .padding()
            
            Stepper("Age: \(age)",
                    value: $age,
                    in: 0...100
            )
            .padding()
            
            HStack() {
                Text("Gender:")
                Spacer()
                Picker("Gender", selection: $gender) {
                    Text("Male").tag("male")
                    Text("Female").tag("female")
                }
            }
            .padding()
            
            TextField("Height", text: $height)
                .overlay(
                    RoundedRectangle(cornerRadius: 22)
                        .stroke(.primary, lineWidth: 2)
                        .padding(-5)
                        .frame(height: 30)
                )
                .keyboardType(.numberPad)
                .padding()
            
            Spacer()
        }
        .navigationTitle("New DataSet")
    }
}

#Preview {
    newDataSet()
}
