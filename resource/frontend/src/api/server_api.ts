import axios from "axios"
import type { AxiosInstance } from "axios"
import type { AnswerRequest,  AnswerResponse, QuestionData, UISetupResponse,  ConversationsResponse,  ConversationResponse } from "@/models";

export class ServerApi {
    private static _host: string | undefined;
    public static client: AxiosInstance;
    private static initialized = false;
    public static errors: any[] = [];

    static get host(): string | undefined {
        return this._host;
    }

    static set host(value : string | undefined) {
        this._host = value;
        this.client = axios.create({ baseURL: value});
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error(error);
                this.errors.push(error.response);
            }
        )
    }

    public static init(options?: { host?: string;  }) {
        if (this.initialized) return
        
        if (options) {
            const { host } = options;
            this.host = host;
        }

        this.initialized = true;
    }
    public static async getUISetup() {
        const responseData = await this.client.get<UISetupResponse>(`/api/config/get_ui_setup`);
        return responseData?.data;
    }

    public static async getUserConversations() {
        const responseData = await this.client.get<ConversationsResponse>("/api/conversation/conversations");
        console.debug(responseData?.data)
        return responseData?.data;
    }

    public static async getConversation(id: string) {
        const responseData = await this.client.get<ConversationResponse>(`/api/conversation/${id}`);
        return responseData?.data
    }

    public static async getAnswer(data : AnswerRequest) {
        const responseData = await this.client.post<AnswerResponse>(`/api/answer/get_answer`, data);
        return responseData?.data;
    }

    public static async clearHistory(id: string) {
        await this.client.delete(`/api/conversation/${id}/history`);
        return true;
    }

    public static async deleteConversation(id: string) {
        await this.client.delete(`/api/conversation/${id}`);
        return true;
    }

    public static async deleteAllConversations() {
        await this.client.delete(`/api/conversation/conversations`);
        return true;
    }

    public static async logFeedback(conversation_id: string, record_id: number | string, data: QuestionData) {
        await this.client.post(`/api/conversation/${conversation_id}/records/${String(record_id)}/log_feedback`, data);
        return true;
    }

}