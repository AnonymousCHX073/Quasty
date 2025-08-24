(function(Scratch) {
  "use strict";
  
  class QuastySafety {
    constructor() {
      // 初始化存储和状态
      this.rules = [];
      this.lastResult = null;
      this.securityLevel = "medium";
      this.logs = [];
    }
    
    getInfo() {
      return {
        id: 'quastySafety',
        name: 'Quasty Safety',
        color1: '#01538D',
        color2: '#F3CC15',
        color3: '#F3CC15',
        blocks: [
          // 基础过滤功能
          {
            opcode: 'ban',
            blockType: Scratch.BlockType.REPORTER,
            text: '过滤HTML [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '输入内容'
              }
            }
          },
          {
            opcode: 'test',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '检测危险内容 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'example.com'
              }
            }
          },
          {
            opcode: 'banex',
            blockType: Scratch.BlockType.REPORTER,
            text: '严格过滤 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'malicious-code'
              }
            }
          },
          
          // 内容验证
          {
            opcode: 'validateEmail',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '验证邮箱格式 [email]',
            arguments: {
              email: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'user@example.com'
              }
            }
          },
          {
            opcode: 'validateURL',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '验证URL格式 [url]',
            arguments: {
              url: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'https://example.com'
              }
            }
          },
          {
            opcode: 'validatePassword',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '验证密码强度 [password]',
            arguments: {
              password: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'password123'
              }
            }
          },
          
          // 编码/解码
          {
            opcode: 'encodeHTML',
            blockType: Scratch.BlockType.REPORTER,
            text: 'HTML编码 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '<script>'
              }
            }
          },
          {
            opcode: 'encodeURL',
            blockType: Scratch.BlockType.REPORTER,
            text: 'URL编码 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'query string'
              }
            }
          },
          {
            opcode: 'encodeBase64',
            blockType: Scratch.BlockType.REPORTER,
            text: 'Base64编码 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'encode me'
              }
            }
          },
          
          // 安全工具
          {
            opcode: 'generateToken',
            blockType: Scratch.BlockType.REPORTER,
            text: '生成安全令牌 [length]',
            arguments: {
              length: {
                type: Scratch.ArgumentType.NUMBER,
                defaultValue: 16
              }
            }
          },
          {
            opcode: 'hashContent',
            blockType: Scratch.BlockType.REPORTER,
            text: '哈希内容 [content] 使用 [algorithm]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'hash this'
              },
              algorithm: {
                type: Scratch.ArgumentType.STRING,
                menu: 'hashAlgorithmMenu'
              }
            }
          },
          {
            opcode: 'checkPrivacy',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '检查隐私泄露 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'email@example.com'
              }
            }
          },
          
          // 安全配置
          {
            opcode: 'setSecurityLevel',
            blockType: Scratch.BlockType.COMMAND,
            text: '设置安全级别为 [level]',
            arguments: {
              level: {
                type: Scratch.ArgumentType.STRING,
                menu: 'securityLevelMenu'
              }
            }
          },
          {
            opcode: 'addAllowedDomain',
            blockType: Scratch.BlockType.COMMAND,
            text: '添加允许的域名 [domain]',
            arguments: {
              domain: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'example.com'
              }
            }
          },
          {
            opcode: 'addBlockedPattern',
            blockType: Scratch.BlockType.COMMAND,
            text: '添加阻止模式 [pattern]',
            arguments: {
              pattern: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'malicious'
              }
            }
          },
          
          // 日志和监控
          {
            opcode: 'logEvent',
            blockType: Scratch.BlockType.COMMAND,
            text: '记录安全事件 [event]',
            arguments: {
              event: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '安全事件'
              }
            }
          },
          {
            opcode: 'getLastEvent',
            blockType: Scratch.BlockType.REPORTER,
            text: '获取最后事件'
          },
          {
            opcode: 'clearLogs',
            blockType: Scratch.BlockType.COMMAND,
            text: '清除日志'
          },
          
          // 实用工具
          {
            opcode: 'nop',
            blockType: Scratch.BlockType.REPORTER,
            text: '无操作返回 [content]',
            arguments: {
              content: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'input'
              }
            }
          },
          {
            opcode: 'close',
            blockType: Scratch.BlockType.COMMAND,
            text: '关闭安全扩展'
          }
        ],
        menus: {
          hashAlgorithmMenu: {
            items: ['MD5', 'SHA-1', 'SHA-256', 'SHA-512']
          },
          securityLevelMenu: {
            items: ['low', 'medium', 'high', 'paranoid']
          }
        }
      };
    }
    
    // 基础过滤功能
    ban(args) {
      const input = args.content;
      if (!input || typeof input !== 'string') return '';
      
      let output = input
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
        .replace(/on\w+=\s*"[^"]*"/gi, '')
        .replace(/on\w+=\s*'[^']*'/gi, '')
        .replace(/on\w+=\s*[^"'\s][^\s>]*/gi, '')
        .replace(/javascript:\s*[^"'\s]*/gi, '');
      
      this.lastResult = output;
      this.logEvent(`过滤HTML内容: ${input.substring(0, 50)}...`);
      return output;
    }
    
    test(args) {
      const input = args.content;
      if (!input || typeof input !== 'string') return true;
      
      const dangerousPatterns = [
        /<script\b/i,
        /<iframe\b/i,
        /javascript:\s*/i,
        /onload\s*=/i,
        /onerror\s*=/i,
        /onclick\s*=/i,
        /eval\s*\(/i,
        /alert\s*\(/i,
        /document\.cookie/i,
        /window\.location/i
      ];
      
      for (const pattern of dangerousPatterns) {
        if (pattern.test(input)) {
          this.lastResult = false;
          this.logEvent(`检测到危险内容: ${input.substring(0, 50)}...`);
          return false;
        }
      }
      
      this.lastResult = true;
      return true;
    }
    
    banex(args) {
      const input = args.content;
      if (!input || typeof input !== 'string') return '';
      
      let output = input
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/'/g, '&#x27;')
        .replace(/"/g, '&quot;')
        .replace(/\//g, '&#x2F;');
      
      this.lastResult = output;
      this.logEvent(`严格过滤内容: ${input.substring(0, 50)}...`);
      return output;
    }
    
    // 内容验证
    validateEmail(args) {
      const email = args.email;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const isValid = emailRegex.test(email);
      this.logEvent(`验证邮箱: ${email} - ${isValid ? '有效' : '无效'}`);
      return isValid;
    }
    
    validateURL(args) {
      const url = args.url;
      try {
        new URL(url);
        this.logEvent(`验证URL: ${url} - 有效`);
        return true;
      } catch (e) {
        this.logEvent(`验证URL: ${url} - 无效`);
        return false;
      }
    }
    
    validatePassword(args) {
      const password = args.password;
      // 检查密码强度
      const hasMinLength = password.length >= 8;
      const hasUpperCase = /[A-Z]/.test(password);
      const hasLowerCase = /[a-z]/.test(password);
      const hasNumbers = /\d/.test(password);
      const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
      
      const isValid = hasMinLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar;
      this.logEvent(`验证密码强度: ${isValid ? '强' : '弱'}`);
      return isValid;
    }
    
    // 编码/解码
    encodeHTML(args) {
      const content = args.content;
      const encoded = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
      
      this.logEvent(`HTML编码: ${content.substring(0, 30)}...`);
      return encoded;
    }
    
    encodeURL(args) {
      const content = args.content;
      const encoded = encodeURIComponent(content);
      this.logEvent(`URL编码: ${content.substring(0, 30)}...`);
      return encoded;
    }
    
    encodeBase64(args) {
      const content = args.content;
      // 简单的Base64编码（实际应用中应使用btoa）
      const encoded = btoa(unescape(encodeURIComponent(content)));
      this.logEvent(`Base64编码: ${content.substring(0, 30)}...`);
      return encoded;
    }
    
    // 安全工具
    generateToken(args) {
      const length = Math.max(8, Math.min(64, args.length));
      const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
      let token = '';
      
      for (let i = 0; i < length; i++) {
        token += charset.charAt(Math.floor(Math.random() * charset.length));
      }
      
      this.logEvent(`生成长度为${length}的安全令牌`);
      return token;
    }
    
    hashContent(args) {
      const content = args.content;
      const algorithm = args.algorithm;
      
      // 简单模拟哈希函数（实际应用中应使用真正的哈希函数）
      let hash = 0;
      for (let i = 0; i < content.length; i++) {
        hash = ((hash << 5) - hash) + content.charCodeAt(i);
        hash |= 0;
      }
      
      const result = `${algorithm}-${Math.abs(hash).toString(16)}`;
      this.logEvent(`使用${algorithm}哈希内容: ${content.substring(0, 30)}...`);
      return result;
    }
    
    checkPrivacy(args) {
      const content = args.content;
      
      // 检查可能的隐私数据
      const patterns = [
        /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/, // 电话号码
        /\b\d{3}[-.]?\d{2}[-.]?\d{4}\b/, // SSN
        /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i, // 邮箱
        /\b\d{4}[-.]?\d{4}[-.]?\d{4}[-.]?\d{4}\b/ // 信用卡
      ];
      
      const hasPrivacyData = patterns.some(pattern => pattern.test(content));
      this.logEvent(`隐私检查: ${hasPrivacyData ? '发现潜在隐私数据' : '未发现隐私数据'}`);
      return hasPrivacyData;
    }
    
    // 安全配置
    setSecurityLevel(args) {
      this.securityLevel = args.level;
      this.logEvent(`设置安全级别为: ${this.securityLevel}`);
    }
    
    addAllowedDomain(args) {
      const domain = args.domain;
      this.rules.push({ type: 'allowed', value: domain });
      this.logEvent(`添加允许的域名: ${domain}`);
    }
    
    addBlockedPattern(args) {
      const pattern = args.pattern;
      this.rules.push({ type: 'blocked', value: pattern });
      this.logEvent(`添加阻止的模式: ${pattern}`);
    }
    
    // 日志和监控
    logEvent(args) {
      const event = typeof args === 'string' ? args : args.event;
      const timestamp = new Date().toISOString();
      this.logs.push(`${timestamp}: ${event}`);
      
      // 保持日志数量可控
      if (this.logs.length > 100) {
        this.logs.shift();
      }
    }
    
    getLastEvent() {
      return this.logs.length > 0 ? this.logs[this.logs.length - 1] : '无事件记录';
    }
    
    clearLogs() {
      this.logs = [];
      this.logEvent('清除所有日志');
    }
    
    // 实用工具
    nop(args) {
      const content = args.content;
      this.logEvent(`无操作返回: ${content.substring(0, 30)}...`);
      return content;
    }
    
    close() {
      this.rules = [];
      this.lastResult = null;
      this.logEvent('关闭安全扩展');
    }
  }
  
  Scratch.extensions.register(new QuastySafety());
})(Scratch);