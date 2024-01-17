import type { QuestionData } from ".";

export interface ConversationInfo {
    id: string;
    name: string;
    timestamp: number;
}

export interface Conversation extends ConversationInfo {
    auth_identifier: string;
    data: QuestionData[];
}
