import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { Quasar, Notify, Loading, Dialog } from "quasar";
import { QuasarBs } from "quasar-ui-bs";
import "@quasar/extras/material-icons/material-icons.css";
import "@quasar/extras/material-icons-outlined/material-icons-outlined.css";
import "@quasar/extras/material-icons-round/material-icons-round.css";
import "quasar/src/css/index.sass";
import "quasar-ui-bs/style.css";
import "@/assets/css/main.scss";
import 'prismjs/themes/prism-tomorrow.css'
import App from './App.vue';
import router from './router';
import i18n from './i18n';
import { setCssVar } from 'quasar';
import { registerDirectives } from './directives/register';

// load prism components
import 'prismjs/components/prism-javascript'; // JavaScript
import 'prismjs/components/prism-typescript'; // TypeScript
import 'prismjs/components/prism-css'; // CSS
import 'prismjs/components/prism-scss'; // SCSS
import 'prismjs/components/prism-json'; // JSON
import 'prismjs/components/prism-markup'; // XML, HTML, SVG, MathML, etc.
import 'prismjs/components/prism-bash'; // Bash/Shell
import 'prismjs/components/prism-python'; // Python
import 'prismjs/components/prism-java'; // Java
import 'prismjs/components/prism-csharp'; // C#
import 'prismjs/components/prism-c'; // C
import 'prismjs/components/prism-cpp'; // C++


function setColors() {
    setCssVar("primary", "#3B99FC");
}

const app = createApp(App)

setColors();

app.use(createPinia())
app.use(router)
registerDirectives(app);
app.use(Quasar, {
    plugins: {
        Notify,
        Loading,
        Dialog
    }
})
app.use(QuasarBs);
app.use(i18n);

app.mount('#app')