import type { ConversationInfo, Conversation } from "./conversation";

export enum ResponseStatus {
    KO = "ko",
    OK = "ok"
}

export interface Source {
    excerpt: string;
    metadata: Record<string, string | number | any[]>
}
export type FiltersData = { [key: string]: (string | number)[] }

export type FilterConfig = {
    input_dataset: string;
    filter_columns: string[];
    filter_options: Record<string, any[]>;
}

export type UIData = {
    examples: string[];
    title: string;
    subtitle: string;
    language: string;
    input_placeholder: string;
    docs_folder_id: string;
    project: string;
    feedback_negative_choices: string[];
    feedback_positive_choices: string[];
    filters_config: FilterConfig | null;
    knowledge_bank: {knowledge_bank_id: string, knowledge_bank_name: string} | null;

}
export interface AnswerData {
    answer: string;
    sources: Source[];
    conversation_infos: ConversationInfo;
    filters: FiltersData | null;
    record_id: string | number;
}

export interface FiltersRequest {
    query: string;
}

export interface ConvTitleRequest {
    query: string;
    answer: string;
}

interface ServerResponse<T> {
    status: ResponseStatus;
    data: T
}

export interface AnswerRequest {
    conversation_id: string | null;
    query: string;
    filters?: FiltersData | null;
    knowledge_bank_id?: string | null;
}

export enum FeedbackValue {
    NEGATIVE = "NEGATIVE",
    POSITIVE = "POSITIVE"
}

export interface Feedback {
    value: FeedbackValue;
    choice?: string[];
    message?: string | null;
}

export interface QuestionData {
    id: string;
    query: string;
    filters?: FiltersData | null;
    answer: string;
    sources: Source[]
    feedback: Feedback | null;
}

export type LogFeedbackResponse = ServerResponse<number>;
export type FiltersResponse = ServerResponse<FiltersData>;
export type UISetupResponse = ServerResponse<UIData>;
export type AnswerResponse = ServerResponse<AnswerData>;
export type ConversationsResponse = ServerResponse<ConversationInfo[]>;
export type ConversationResponse = ServerResponse<Conversation>;
export type ConversationTitleResponse = ServerResponse<{ title: string; }>
