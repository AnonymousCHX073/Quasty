#include <iostream>
#include <string>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <iomanip>
#include <sstream>

using namespace std;

// 常量定义
const string VERSION = "1.0.0";
const string SPECIAL_CHARACTERS = "!@#$%^&*()_-+=[]{}|;:,.<>?`~";
const string LOWERCASE_LETTERS = "abcdefghijklmnopqrstuvwxyz";
const string UPPERCASE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const string DIGITS = "0123456789";

// 元音和辅音，用于生成可发音密码
const string VOWELS = "aeiouyAEIOUY";
const string CONSONANTS = "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ";

// 常见单词列表，用于生成基于字典的密码
const vector<string> COMMON_WORDS = {
    "apple", "banana", "cherry", "date", "elderberry",
    "friend", "guitar", "happy", "igloo", "jungle",
    "kangaroo", "lemon", "mountain", "nature", "ocean",
    "penguin", "quilt", "rabbit", "sunshine", "tiger",
    "umbrella", "victory", "water", "xylophone", "yellow", "zebra"
};

// 函数声明
void displayWelcomeMessage();
void displayMainMenu();
int getUserChoice(int min, int max);
int getPasswordLength();
int getNumberOfPasswords();
string getOutputFileName();
bool confirmAction(const string& message);

// 密码生成函数
string generateNumericPassword(int length);
string generateAlphaPassword(int length);
string generateAlphaNumericPassword(int length);
string generatePasswordWithSpecialChars(int length);
string generateCryptographicallySecurePassword(int length);
string generatePronounceablePassword(int length);
string generateDictionaryBasedPassword(int wordCount, bool capitalize, bool addNumbers, bool addSymbols);
string generateCustomCharsetPassword(int length, const string& charset);
string generatePatternBasedPassword(const string& pattern);

// 辅助功能函数
int calculatePasswordStrength(const string& password);
void displayPasswordStrength(int strength);
void savePasswordsToFile(const vector<string>& passwords, const string& filename);
string getCustomCharacterSet();
string getPasswordPattern();
void displayAboutInfo();
void displayHelpInfo();

// 主函数
int main() {
    // 初始化随机数生成器
    srand(static_cast<unsigned int>(time(0)));
    
    int choice;
    int length;
    int count;
    vector<string> passwords;
    
    displayWelcomeMessage();
    
    do {
        displayMainMenu();
        choice = getUserChoice(1, 10);
        
        if (choice == 10) {
            // 退出程序
            cout << "感谢使用密码生成器，再见！" << endl;
            break;
        }
        
        // 根据选择处理不同的密码生成方式
        switch (choice) {
            case 1: // 纯数字密码
                length = getPasswordLength();
                count = getNumberOfPasswords();
                cout << "\n生成的纯数字密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generateNumericPassword(length);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
                
            case 2: // 纯字母密码
                length = getPasswordLength();
                count = getNumberOfPasswords();
                cout << "\n生成的纯字母密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generateAlphaPassword(length);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
                
            case 3: // 字母数字混合密码
                length = getPasswordLength();
                count = getNumberOfPasswords();
                cout << "\n生成的字母数字混合密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generateAlphaNumericPassword(length);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
                
            case 4: // 包含特殊字符的密码
                length = getPasswordLength();
                count = getNumberOfPasswords();
                cout << "\n生成的包含特殊字符的密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generatePasswordWithSpecialChars(length);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
                
            case 5: // 密码学安全密码
                length = getPasswordLength();
                // 密码学安全密码建议长度至少为12
                while (length < 12) {
                    cout << "为了保证安全性，密码学安全密码建议长度至少为12位。" << endl;
                    length = getPasswordLength();
                }
                count = getNumberOfPasswords();
                cout << "\n生成的密码学安全密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generateCryptographicallySecurePassword(length);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
                
            case 6: // 可发音密码
                length = getPasswordLength();
                // 可发音密码不宜过短
                while (length < 6) {
                    cout << "可发音密码建议长度至少为6位。" << endl;
                    length = getPasswordLength();
                }
                count = getNumberOfPasswords();
                cout << "\n生成的可发音密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generatePronounceablePassword(length);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
                
            case 7: // 基于字典的密码
            {
                int wordCount;
                cout << "请输入要使用的单词数量（2-5）：";
                wordCount = getUserChoice(2, 5);
                
                bool capitalize, addNumbers, addSymbols;
                
                cout << "是否将单词首字母大写？（1=是，0=否）：";
                capitalize = (getUserChoice(0, 1) == 1);
                
                cout << "是否添加数字？（1=是，0=否）：";
                addNumbers = (getUserChoice(0, 1) == 1);
                
                cout << "是否添加特殊符号？（1=是，0=否）：";
                addSymbols = (getUserChoice(0, 1) == 1);
                
                count = getNumberOfPasswords();
                cout << "\n生成的基于字典的密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generateDictionaryBasedPassword(wordCount, capitalize, addNumbers, addSymbols);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
            }
                
            case 8: // 自定义字符集密码
            {
                string charset = getCustomCharacterSet();
                if (charset.empty()) {
                    cout << "无效的字符集，返回主菜单。" << endl;
                    break;
                }
                
                length = getPasswordLength();
                count = getNumberOfPasswords();
                cout << "\n使用自定义字符集生成的密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generateCustomCharsetPassword(length, charset);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
            }
                
            case 9: // 基于模式的密码
            {
                string pattern = getPasswordPattern();
                count = getNumberOfPasswords();
                cout << "\n基于模式生成的密码如下：" << endl;
                for (int i = 0; i < count; i++) {
                    string password = generatePatternBasedPassword(pattern);
                    passwords.push_back(password);
                    cout << "密码 " << (i + 1) << ": " << password << endl;
                }
                break;
            }
                
            default:
                cout << "无效的选择，请重试。" << endl;
                break;
        }
        
        // 如果生成了密码，提供额外选项
        if (choice >= 1 && choice <= 9 && !passwords.empty()) {
            // 显示每个密码的强度
            cout << "\n密码强度评估：" << endl;
            for (size_t i = 0; i < passwords.size(); i++) {
                int strength = calculatePasswordStrength(passwords[i]);
                cout << "密码 " << (i + 1) << ": ";
                displayPasswordStrength(strength);
            }
            
            // 询问是否保存密码
            if (confirmAction("是否要将生成的密码保存到文件？")) {
                string filename = getOutputFileName();
                savePasswordsToFile(passwords, filename);
            }
            
            // 清空密码列表，准备下一次生成
            passwords.clear();
        }
        
    } while (true);
    
    return 0;
}

// 显示欢迎信息
void displayWelcomeMessage() {
    cout << "================================================" << endl;
    cout << "           高级密码生成器 v" << VERSION << endl;
    cout << "================================================" << endl;
    cout << "这是一个功能强大的密码生成工具，可以生成多种类型的密码。" << endl;
    cout << "所有生成的密码都是随机的，确保安全性和唯一性。" << endl << endl;
}

// 显示主菜单
void displayMainMenu() {
    cout << "请选择密码生成方式：" << endl;
    cout << "1. 纯数字密码" << endl;
    cout << "2. 纯字母密码（包含大小写）" << endl;
    cout << "3. 字母数字混合密码" << endl;
    cout << "4. 包含特殊字符的密码" << endl;
    cout << "5. 密码学安全密码（高强度）" << endl;
    cout << "6. 可发音密码（易于记忆）" << endl;
    cout << "7. 基于字典的密码" << endl;
    cout << "8. 自定义字符集密码" << endl;
    cout << "9. 基于模式的密码" << endl;
    cout << "10. 退出程序" << endl;
    cout << "请输入选项 (1-10)：";
}

// 获取用户选择，并验证范围
int getUserChoice(int min, int max) {
    int choice;
    bool valid = false;
    
    do {
        cin >> choice;
        
        if (cin.fail()) {
            // 清除错误状态
            cin.clear();
            // 忽略缓冲区中的无效输入
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "输入无效，请输入一个数字：";
        } else if (choice < min || choice > max) {
            cout << "选择超出范围，请输入 " << min << " 到 " << max << " 之间的数字：";
        } else {
            valid = true;
        }
    } while (!valid);
    
    return choice;
}

// 获取密码长度
int getPasswordLength() {
    int length;
    cout << "请输入每个密码的位数（建议至少8位）：";
    
    do {
        cin >> length;
        
        if (cin.fail()) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "输入无效，请输入一个数字：";
        } else if (length <= 0) {
            cout << "密码位数必须大于0，请重新输入：";
        } else if (length < 8) {
            if (confirmAction("密码长度小于8位，安全性较低，是否继续？")) {
                break;
            } else {
                cout << "请输入每个密码的位数：";
            }
        } else {
            break;
        }
    } while (true);
    
    return length;
}

// 获取要生成的密码数量
int getNumberOfPasswords() {
    int count;
    cout << "请输入要生成的密码数量：";
    
    do {
        cin >> count;
        
        if (cin.fail()) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "输入无效，请输入一个数字：";
        } else if (count <= 0) {
            cout << "密码数量必须大于0，请重新输入：";
        } else if (count > 100) {
            if (confirmAction("生成超过100个密码可能需要一些时间，是否继续？")) {
                break;
            } else {
                cout << "请输入要生成的密码数量：";
            }
        } else {
            break;
        }
    } while (true);
    
    return count;
}

// 获取输出文件名
string getOutputFileName() {
    string filename;
    cout << "请输入保存密码的文件名（默认为passwords.txt）：";
    cin.ignore(); // 忽略之前输入留下的换行符
    getline(cin, filename);
    
    if (filename.empty()) {
        filename = "passwords.txt";
    }
    
    // 确保文件有.txt扩展名
    if (filename.find(".txt") == string::npos) {
        filename += ".txt";
    }
    
    return filename;
}

// 确认操作
bool confirmAction(const string& message) {
    cout << message << "（1=是，0=否）：";
    return (getUserChoice(0, 1) == 1);
}

// 生成纯数字密码
string generateNumericPassword(int length) {
    string password;
    
    for (int i = 0; i < length; i++) {
        password += DIGITS[rand() % DIGITS.size()];
    }
    
    return password;
}

// 生成纯字母密码（包含大小写）
string generateAlphaPassword(int length) {
    string password;
    string letters = LOWERCASE_LETTERS + UPPERCASE_LETTERS;
    
    for (int i = 0; i < length; i++) {
        password += letters[rand() % letters.size()];
    }
    
    return password;
}

// 生成字母数字混合密码
string generateAlphaNumericPassword(int length) {
    string password;
    string chars = LOWERCASE_LETTERS + UPPERCASE_LETTERS + DIGITS;
    
    for (int i = 0; i < length; i++) {
        password += chars[rand() % chars.size()];
    }
    
    return password;
}

// 生成包含特殊字符的密码
string generatePasswordWithSpecialChars(int length) {
    string password;
    string chars = LOWERCASE_LETTERS + UPPERCASE_LETTERS + DIGITS + SPECIAL_CHARACTERS;
    
    // 确保至少包含一个特殊字符
    if (length >= 4) {
        // 先添加各类字符各一个，保证多样性
        password += LOWERCASE_LETTERS[rand() % LOWERCASE_LETTERS.size()];
        password += UPPERCASE_LETTERS[rand() % UPPERCASE_LETTERS.size()];
        password += DIGITS[rand() % DIGITS.size()];
        password += SPECIAL_CHARACTERS[rand() % SPECIAL_CHARACTERS.size()];
        
        // 生成剩余字符
        for (int i = 4; i < length; i++) {
            password += chars[rand() % chars.size()];
        }
        
        // 打乱密码顺序
        random_shuffle(password.begin(), password.end());
    } else {
        // 对于短密码，直接随机生成
        for (int i = 0; i < length; i++) {
            password += chars[rand() % chars.size()];
        }
    }
    
    return password;
}

// 生成密码学安全密码（更高强度，确保包含各类字符）
string generateCryptographicallySecurePassword(int length) {
    string password;
    string lowercase = LOWERCASE_LETTERS;
    string uppercase = UPPERCASE_LETTERS;
    string digits = DIGITS;
    string special = SPECIAL_CHARACTERS;
    
    // 确保至少包含每种类型的字符各一个
    password += lowercase[rand() % lowercase.size()];
    password += uppercase[rand() % uppercase.size()];
    password += digits[rand() % digits.size()];
    password += special[rand() % special.size()];
    
    // 剩余字符从所有字符集中随机选择
    string allChars = lowercase + uppercase + digits + special;
    for (int i = 4; i < length; i++) {
        password += allChars[rand() % allChars.size()];
    }
    
    // 多次打乱密码顺序，增加随机性
    for (int i = 0; i < 3; i++) {
        random_shuffle(password.begin(), password.end());
    }
    
    return password;
}

// 生成可发音密码（交替使用元音和辅音）
string generatePronounceablePassword(int length) {
    string password;
    bool useVowel = (rand() % 2 == 0); // 随机决定从元音还是辅音开始
    
    for (int i = 0; i < length; i++) {
        if (useVowel) {
            password += VOWELS[rand() % VOWELS.size()];
        } else {
            password += CONSONANTS[rand() % CONSONANTS.size()];
        }
        
        // 有20%的概率不切换类型，增加一些变化
        if (rand() % 5 != 0) {
            useVowel = !useVowel;
        }
    }
    
    return password;
}

// 生成基于字典的密码
string generateDictionaryBasedPassword(int wordCount, bool capitalize, bool addNumbers, bool addSymbols) {
    string password;
    vector<string> selectedWords;
    
    // 确保不会重复选择同一个单词
    vector<string> availableWords = COMMON_WORDS;
    
    // 选择指定数量的单词
    for (int i = 0; i < wordCount && !availableWords.empty(); i++) {
        int index = rand() % availableWords.size();
        string word = availableWords[index];
        
        // 如果需要，将首字母大写
        if (capitalize && !word.empty()) {
            word[0] = toupper(word[0]);
        }
        
        selectedWords.push_back(word);
        
        // 从可用单词列表中移除已选择的单词
        availableWords.erase(availableWords.begin() + index);
    }
    
    // 如果可用单词不足，用随机字符补充
    while (selectedWords.size() < static_cast<size_t>(wordCount)) {
        string randomWord;
        int wordLength = 3 + rand() % 5; // 3-7个字符
        for (int i = 0; i < wordLength; i++) {
            randomWord += LOWERCASE_LETTERS[rand() % LOWERCASE_LETTERS.size()];
        }
        if (capitalize) {
            randomWord[0] = toupper(randomWord[0]);
        }
        selectedWords.push_back(randomWord);
    }
    
    // 打乱单词顺序
    random_shuffle(selectedWords.begin(), selectedWords.end());
    
    // 连接单词
    for (const string& word : selectedWords) {
        password += word;
    }
    
    // 可选：添加数字
    if (addNumbers) {
        int numDigits = 1 + rand() % 3; // 1-3个数字
        string numbers;
        for (int i = 0; i < numDigits; i++) {
            numbers += DIGITS[rand() % DIGITS.size()];
        }
        
        // 随机插入数字
        int insertPos = rand() % (password.length() + 1);
        password.insert(insertPos, numbers);
    }
    
    // 可选：添加特殊符号
    if (addSymbols) {
        int numSymbols = 1 + rand() % 2; // 1-2个符号
        string symbols;
        for (int i = 0; i < numSymbols; i++) {
            symbols += SPECIAL_CHARACTERS[rand() % SPECIAL_CHARACTERS.size()];
        }
        
        // 随机插入符号
        int insertPos = rand() % (password.length() + 1);
        password.insert(insertPos, symbols);
    }
    
    return password;
}

// 获取自定义字符集
string getCustomCharacterSet() {
    string charset;
    cout << "请输入自定义字符集（例如：abc123!@#）：";
    cin.ignore(); // 忽略之前的换行符
    getline(cin, charset);
    
    // 移除重复字符
    sort(charset.begin(), charset.end());
    auto last = unique(charset.begin(), charset.end());
    charset.erase(last, charset.end());
    
    if (charset.empty()) {
        cout << "字符集不能为空！" << endl;
        return "";
    }
    
    cout << "已去除重复字符，使用的字符集为：" << charset << endl;
    return charset;
}

// 生成自定义字符集密码
string generateCustomCharsetPassword(int length, const string& charset) {
    string password;
    
    for (int i = 0; i < length; i++) {
        password += charset[rand() % charset.size()];
    }
    
    return password;
}

// 获取密码模式
string getPasswordPattern() {
    cout << "请输入密码模式，使用以下占位符：" << endl;
    cout << "  a - 小写字母" << endl;
    cout << "  A - 大写字母" << endl;
    cout << "  0 - 数字" << endl;
    cout << "  # - 特殊字符" << endl;
    cout << "  其他字符将原样保留" << endl;
    cout << "例如：\"Aa0#Aa0#\" 将生成8位密码，包含大小写字母、数字和特殊字符各2个" << endl;
    cout << "请输入密码模式：";
    
    string pattern;
    cin.ignore();
    getline(cin, pattern);
    
    if (pattern.empty()) {
        cout << "模式不能为空，将使用默认模式：\"Aa0#Aa0#\"" << endl;
        return "Aa0#Aa0#";
    }
    
    return pattern;
}

// 生成基于模式的密码
string generatePatternBasedPassword(const string& pattern) {
    string password;
    
    for (char c : pattern) {
        switch (c) {
            case 'a': // 小写字母
                password += LOWERCASE_LETTERS[rand() % LOWERCASE_LETTERS.size()];
                break;
            case 'A': // 大写字母
                password += UPPERCASE_LETTERS[rand() % UPPERCASE_LETTERS.size()];
                break;
            case '0': // 数字
                password += DIGITS[rand() % DIGITS.size()];
                break;
            case '#': // 特殊字符
                password += SPECIAL_CHARACTERS[rand() % SPECIAL_CHARACTERS.size()];
                break;
            default: // 其他字符原样保留
                password += c;
                break;
        }
    }
    
    return password;
}

// 计算密码强度（0-100）
int calculatePasswordStrength(const string& password) {
    int strength = 0;
    int length = password.length();
    
    // 基于长度的评分（最高30分）
    if (length >= 16) {
        strength += 30;
    } else if (length >= 12) {
        strength += 25;
    } else if (length >= 8) {
        strength += 20;
    } else if (length >= 6) {
        strength += 10;
    } else {
        strength += 5;
    }
    
    bool hasLower = false, hasUpper = false, hasDigit = false, hasSpecial = false;
    
    // 检查密码包含的字符类型
    for (char c : password) {
        if (islower(c)) hasLower = true;
        else if (isupper(c)) hasUpper = true;
        else if (isdigit(c)) hasDigit = true;
        else if (SPECIAL_CHARACTERS.find(c) != string::npos) hasSpecial = true;
    }
    
    // 基于字符类型多样性的评分（最高40分）
    int typeCount = 0;
    if (hasLower) typeCount++;
    if (hasUpper) typeCount++;
    if (hasDigit) typeCount++;
    if (hasSpecial) typeCount++;
    
    switch (typeCount) {
        case 4: strength += 40; break;
        case 3: strength += 30; break;
        case 2: strength += 15; break;
        case 1: strength += 5; break;
        default: break;
    }
    
    // 检查字符分布均匀性（最高20分）
    int lowerCount = 0, upperCount = 0, digitCount = 0, specialCount = 0;
    for (char c : password) {
        if (islower(c)) lowerCount++;
        else if (isupper(c)) upperCount++;
        else if (isdigit(c)) digitCount++;
        else if (SPECIAL_CHARACTERS.find(c) != string::npos) specialCount++;
    }
    
    // 计算标准差，值越小表示分布越均匀
    double mean = static_cast<double>(length) / typeCount;
    double variance = 0;
    
    if (hasLower) variance += pow(lowerCount - mean, 2);
    if (hasUpper) variance += pow(upperCount - mean, 2);
    if (hasDigit) variance += pow(digitCount - mean, 2);
    if (hasSpecial) variance += pow(specialCount - mean, 2);
    
    variance /= typeCount;
    double stdDev = sqrt(variance);
    
    // 标准差越小，得分越高（最高20分）
    int distributionScore = max(0, 20 - static_cast<int>(stdDev * 2));
    strength += distributionScore;
    
    // 检查是否有常见模式（最高扣10分）
    string lowerPassword = password;
    transform(lowerPassword.begin(), lowerPassword.end(), lowerPassword.begin(), ::tolower);
    
    // 检查连续字符
    bool hasSequential = false;
    for (int i = 0; i < length - 2; i++) {
        if (lowerPassword[i+1] == lowerPassword[i] + 1 && 
            lowerPassword[i+2] == lowerPassword[i] + 2) {
            hasSequential = true;
            break;
        }
    }
    
    // 检查重复字符
    bool hasRepeating = false;
    for (int i = 0; i < length - 1; i++) {
        if (lowerPassword[i] == lowerPassword[i+1]) {
            hasRepeating = true;
            break;
        }
    }
    
    if (hasSequential || hasRepeating) {
        strength = max(0, strength - 10);
    }
    
    // 确保强度在0-100范围内
    return max(0, min(100, strength));
}

// 显示密码强度
void displayPasswordStrength(int strength) {
    if (strength >= 90) {
        cout << "极强 (" << strength << "/100)" << endl;
    } else if (strength >= 70) {
        cout << "强 (" << strength << "/100)" << endl;
    } else if (strength >= 50) {
        cout << "中等 (" << strength << "/100)" << endl;
    } else if (strength >= 30) {
        cout << "弱 (" << strength << "/100)" << endl;
    } else {
        cout << "极弱 (" << strength << "/100)" << endl;
    }
}

// 保存密码到文件
void savePasswordsToFile(const vector<string>& passwords, const string& filename) {
    ofstream outFile(filename);
    
    if (!outFile.is_open()) {
        cout << "无法打开文件 " << filename << " 进行写入！" << endl;
        return;
    }
    
    // 写入文件头部信息
    time_t now = time(0);
    tm* localTime = localtime(&now);
    outFile << "密码生成记录 - " << asctime(localTime);
    outFile << "共 " << passwords.size() << " 个密码" << endl;
    outFile << "============================================" << endl << endl;
    
    // 写入密码
    for (size_t i = 0; i < passwords.size(); i++) {
        outFile << "密码 " << (i + 1) << ": " << passwords[i] << endl;
    }
    
    outFile.close();
    cout << "密码已成功保存到文件：" << filename << endl;
}
