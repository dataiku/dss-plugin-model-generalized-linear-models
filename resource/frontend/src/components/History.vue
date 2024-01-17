<template>
  <div class="chat-container">
    <BsButton
      no-caps
      class="bs-font-medium-2-normal"
      unelevated
      textColor="primary"
      @click="startNewChat"
      >New Chat</BsButton
    >
    <div class="chat-list">
      <div v-for="chat in chats" :key="chat.id" class="chat-session" @click="selectChat(chat)">
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { BsDrawer } from 'quasar-ui-bs'

export default {
  components: { BsDrawer },
  data() {
    return {
      currentQuery: null,
      queriesAnswers: [],
      chats: [
        { id: 1, text: 'Chat session 1' }
      ]
    }
  },
  methods: {
    startNewChat() {
      // Logic to start a new chat
    },
    selectChat(chat: any) {
      this.currentQuery = chat
      // Fetch or set the queries-answers related to the selected chat session
      // Example: this.queriesAnswers = fetchChatAnswers(chat.id);
    }
  },
  mounted() {}
}
</script>
<style scoped>
.chat-container {
  max-width: 300px;
  font-family: Arial, sans-serif;
}

button {
  display: block;
  margin-bottom: 10px;
}

.chat-list {
  overflow-y: auto;
  max-height: 400px;
}

.chat-session {
  display: flex;
  align-items: center;
  padding: 5px;
  border: 1px solid #ddd;
  margin-top: 5px;
  overflow: hidden;
  cursor: pointer;
}

.chat-icon {
  width: 20px;
  height: 20px;
  margin-right: 10px;
}

.chat-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
