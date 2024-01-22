import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

// import "@quasar/extras/material-icons/material-icons.css";
// import "@quasar/extras/material-icons-outlined/material-icons-outlined.css";
// import "@quasar/extras/material-icons-round/material-icons-round.css";
// import "@quasar/extras/mdi-v6/mdi-v6.css";
// import "quasar/src/css/index.sass";
// import "quasar-ui-bs/dist/style.css";
// import "vite/modulepreload-polyfill";
import { QuasarBs } from "quasar-ui-bs";

const myApp = createApp(App)

myApp.use(QuasarBs);
myApp.mount('#app')