#include "Domen.hpp"
#include <algorithm>

namespace Domen {

// ---- Host -------------------------------------------------
void Host::admit(const User& /*user*/) { /* TODO: admit logic */ }
void Host::reject(const User& /*user*/) { /* TODO: reject logic */ }

// ---- Conference -------------------------------------------
void Conference::start() { /* TODO */ }
void Conference::end()   { /* TODO */ }

void Conference::addParticipant(User* u) {
    if (!u) return;
    if (std::find(participants.begin(), participants.end(), u) == participants.end())
        participants.push_back(u);
    u->setCurrentConf(this);
}
void Conference::removeParticipant(User* u) {
    if (!u) return;
    participants.erase(std::remove(participants.begin(), participants.end(), u), participants.end());
    if (u->getCurrentConf() == this) u->setCurrentConf(nullptr);
}

// ---- AuthService ------------------------------------------
bool AuthService::checkAccount(const std::string& login) {
    return !login.empty();
}
Token AuthService::login(const Credentials& /*credentials*/) {
    return Token{ "token", std::time(nullptr) + 3600 };
}
Result AuthService::registerUser(const RegistrationForm& /*data*/) {
    return Result::Success;
}

// ---- DeviceCheck ------------------------------------------
DevicesResult DeviceCheck::verify(bool camera, bool mic, bool net) {
    return DevicesResult{ mic, camera, net, "" };
}

// ---- ClientApp --------------------------------------------
void ClientApp::requestJoin() {}
void ClientApp::openInvite() {}
bool ClientApp::connect() { return true; }
void ClientApp::disconnect() {}
void ClientApp::toggleMic() {}
void ClientApp::toggleCamera() {}
void ClientApp::raiseHand() {}
void ClientApp::sendChat(const std::string& /*msg*/) {}
void ClientApp::startShare() {}
void ClientApp::stopShare() {}

bool ClientApp::checkAccount(const std::string& login) {
    return authService ? authService->checkAccount(login) : false;
}
Result ClientApp::registerUser(const RegistrationForm& data) {
    return authService ? authService->registerUser(data) : Result::Fail;
}
DevicesResult ClientApp::verifyDevices() {
    if (deviceCheck) return deviceCheck->verify(true, true, true);
    return DevicesResult{};
}

} // namespace Domen
