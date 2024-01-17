import { createRouter, createWebHistory } from 'vue-router'
import { inIframe } from '@/common/utils'
import HomeView from '../routes/HomeView.vue'
import ConversationView from "../routes/ConversationView.vue";
import PageNotFound from "../views/PageNotFound.vue"
import EmptyStateView from "../routes/EmptyStateView.vue";


function getBase() {
  if (inIframe()) {
    return '/dip/api/webapps/view';
  } else {
      const location = window.location.pathname.match(
          /(\/public-webapps\/[a-zA-Z0-9\-_]*\/[a-zA-Z0-9\-_]*).*/
      );
      return location ? location[1] : '';
  }
}

const router = createRouter({
  history: createWebHistory(getBase()),
  routes: [
    {
      path: '/',
      name: 'root',
      component: HomeView,
      redirect: "/new",
      children: [
        {
          path: "/conversation/:id",
          name: "conversation-item",
          component: ConversationView,
          props: true
        },
        {
          path: "new",
          name: "new-conversation",
          component: EmptyStateView,
          props: () => {
            return { id: null}
          }
        }
    ]

    },
    { path : '/:pathMatch(.*)*', name: "notFound", component: PageNotFound}
  ]
})

export default router
