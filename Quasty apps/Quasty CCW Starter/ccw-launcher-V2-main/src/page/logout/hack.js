console.log('注入');
const interval = setInterval(() => {
    console.log('注入');
    try {
        if (document.getElementsByClassName("c-avatar-img")[0] && document.getElementsByClassName("container-3N3ii")[0].contains(document.getElementsByClassName("c-avatar-img")[0])) {
            clearInterval(interval);
            window.__TAURI_INVOKE__('inject_js_with_delay', {
                value: '../src/page/logout/after.js',
                id: 'logout'
            })
                .then(() => {
                    setTimeout(() => {
                        document.getElementsByClassName("item-13OiL")[8].click();
                    }, 1000);
                });

        }
    } catch (e) {
        console.log(e);
    }
}, 100);