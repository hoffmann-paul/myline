import SwiftUI

struct DataSet: Codable, Identifiable {
    var id: UUID = UUID()
    
    var comment: String
    var name: String
    var age: Int
    var gender: String
    var height: Double
    var weight: Double
    var eyeColor: String
    var hairColor: String
    var bloodType: String
    var phonenumber: String
    var email: String
    var birthday: String
    var nationality: String
    var job: String
    var religion: String
    var handedness: String
    var hobbys: [String]
    
    var socialMedia: SocialMedia
    var passwords: Passwords
    var devices: [Device]
    
    var ipAdress: String
    var browser: String
    var platform: String
    var isp: String
    var cookies: Bool
    var darkmode: Bool
    var languages: [String]
    var timezone: String
    var localPhone: Int
    var screenResolution: String
    
    var coordinates: Coordinates
    var address: Address
    var licensePlate: String
    
    var vegetarien: Bool
    var vegan: Bool
    var glutenFree: Bool
    var lactoseFree: Bool
    var smoker: Bool
    
    var mentalIllness: [String]
    var medications: [String]
    var allergies: [String]
    
    var relationshipStatus: String
    var partnerName: String
    var familyMembers: [FamilyMember]
}

struct SocialMedia: Codable {
    var instagramm: String
    var snapchat: String
    var youtube: String
    var X: String
    var tiktok: String
    var linkedin: String
    var facebook: String
    var pinterest: String
}

struct Passwords: Codable {
    var instagramm: String
    var snapchat: String
    var youtube: String
    var X: String
    var linkedin: String
    var facebook: String
    var pinterest: String
    var email: String
    var mobilePhone: String
    var SIM: Double
}

struct Device: Codable, Identifiable {
    var id: UUID = UUID()
    var type: String
    var model: String
    var os: String
    var macAddress: String
    var serialNumber: String
}

struct Coordinates: Codable {
    var latitude: Double
    var longitude: Double
    var accuracy: String
}

struct Address: Codable {
    var city: String
    var street: String
    var postalCode: String
    var country: String
}

struct FamilyMember: Codable, Identifiable {
    var id: UUID = UUID()
    var name: String
    var relation: String
}
