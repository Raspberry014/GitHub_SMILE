#pragma once
#include <string>
#include <vector>
#include <ctime>

namespace Domen {

enum class UserStatus { Waiting, InConference, Disconnected };
enum class Result { Success, Fail };

struct Credentials {
    std::string login;
    std::string password;
};
struct Token {
    std::string value;
    std::time_t expiresAt{};
};
struct RegistrationForm {
    std::string name;
    std::string email;
    std::string password;
};
struct DevicesResult {
    bool micOk{false};
    bool camOk{false};
    bool netOk{false};
    std::string message;
};

class Conference; class Lobby; class AuthService; class DeviceCheck;

class User {
public:
    User() = default;
    virtual ~User() = default;

    int getId() const { return id; }
    void setId(int v) { id = v; }

    const std::string& getName() const { return name; }
    void setName(const std::string& v) { name = v; }

    UserStatus getStatus() const { return status; }
    void setStatus(UserStatus s) { status = s; }

    Conference* getCurrentConf() const { return currentConf; }
    void setCurrentConf(Conference* c) { currentConf = c; }

private:
    int id{};
    std::string name;
    UserStatus status{UserStatus::Waiting};
    Conference* currentConf{nullptr};
};

class Host : public User {
public:
    void admit(const User& user);
    void reject(const User& user);
};

class Conference {
public:
    void start();
    void end();

    void setHost(Host* h) { host = h; }
    Host* getHost() const { return host; }

    void addParticipant(User* u);
    void removeParticipant(User* u);
    const std::vector<User*>& getParticipants() const { return participants; }

    void setLobby(Lobby* l) { lobby = l; }
    Lobby* getLobby() const { return lobby; }

private:
    Host* host{nullptr};
    std::vector<User*> participants;
    Lobby* lobby{nullptr};
};

class Lobby {
public:
    void setConf(Conference* c) { conf = c; }
    Conference* getConf() const { return conf; }
private:
    Conference* conf{nullptr};
};

class AuthService {
public:
    bool  checkAccount(const std::string& login);
    Token login(const Credentials& credentials);
    Result registerUser(const RegistrationForm& data);
};

class DeviceCheck {
public:
    DevicesResult verify(bool camera, bool mic, bool net);
};

class ClientApp {
public:
    void requestJoin();
    void openInvite();
    bool connect();
    void disconnect();
    void toggleMic();
    void toggleCamera();
    void raiseHand();
    void sendChat(const std::string& msg);
    void startShare();
    void stopShare();

    bool   checkAccount(const std::string& login);
    Result registerUser(const RegistrationForm& data);
    DevicesResult verifyDevices();

    // wiring
    void setAuthService(AuthService* s) { authService = s; }
    void setDeviceCheck(DeviceCheck* d) { deviceCheck = d; }
    void setCurrentConf(Conference* c)  { currentConf = c; }

private:
    AuthService* authService{nullptr};
    DeviceCheck* deviceCheck{nullptr};
    Conference*  currentConf{nullptr};
};

} // namespace Domen
