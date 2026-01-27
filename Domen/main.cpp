#include "Domen.hpp"
#include <iostream>
int main() {
    Domen::AuthService auth;
    Domen::DeviceCheck dev;
    Domen::Conference conf;
    Domen::ClientApp app;
    app.setAuthService(&auth);
    app.setDeviceCheck(&dev);
    app.setCurrentConf(&conf);

    std::cout << "[connect] " << (app.connect() ? "OK" : "FAIL") << "\n";
    std::cout << "[checkAccount] " << (app.checkAccount("user1") ? "exists" : "no") << "\n";
    Domen::DevicesResult d = app.verifyDevices();
    std::cout << "[verifyDevices] mic=" << d.micOk << " cam=" << d.camOk << " net=" << d.netOk << "\n";
    return 0;
}
