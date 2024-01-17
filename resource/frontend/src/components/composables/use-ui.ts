
import { ServerApi } from '@/api/server_api';
import i18n from '@/i18n';
import { ref, onMounted } from 'vue';
import type { FilterConfig } from '@/models';

interface UISetup {
  examples: string[];
  title?: string;
  subtitle?: string;
  questionPlaceholder?: string;
  language?: string;
  projectKey?: string;
  docsFolderId?: string;
  feedbackPositiveChoices?: string[];
  feedbackNegativeChoices?: string[];
  filtersConfig?: FilterConfig | null;
  knowledgeBank?: {id: string, label: string} | null;
}

const infoTextOne = '“Lorem ipsum dolor sit amet, consectetur adipiscing elit”'
const infoTextTwo =
  '“Fusce pulvinar augue quis commodo pharetra, quisque mattis, diam ut tempor egestas”'
const infoTextThree =
  '“Maecenas augue nunc, fermentum ac placerat sed, eleifend eget odio. Nunc ut cursus felis”'

const initExamples = [infoTextOne, infoTextTwo, infoTextThree]

const initUISeup: UISetup = {
  examples: initExamples
}

const setup = ref<UISetup>(initUISeup)

export function useUI() {

  const filtersConfigTest: FilterConfig = {
    input_dataset: "test",
    filter_columns: ["type", "source"],
    filter_options: {
      type: ["html", "py", "js"],
      source: ["https://developer.dataiku.com/latest/", "https://developer.dataiku.com/latest/_downloads/02b9c4dafcae02885d7675a7e16d8074/code.html", "https://developer.dataiku.com/latest/api-reference/python/datasets.html", "https://developer.dataiku.com/latest/api-reference/python/index.html"]
    }
  }

  async function initializeUI() {
    try {
      const response = await ServerApi.getUISetup()
      if (response && response.data) {
        const uiSetup: UISetup = {
          examples: response.data.examples || [],
          title: response.data.title,
          subtitle: response.data.subtitle,
          questionPlaceholder: response.data.input_placeholder,
          projectKey: response.data.project,
          docsFolderId: response.data.docs_folder_id,
          feedbackPositiveChoices: response.data.feedback_positive_choices,
          feedbackNegativeChoices: response.data.feedback_negative_choices,
          filtersConfig: response.data.filters_config,
          knowledgeBank: response.data.knowledge_bank ? {id: response.data.knowledge_bank.knowledge_bank_id, label: response.data.knowledge_bank.knowledge_bank_name} : null,
          //filtersConfig: filtersConfigTest

        }
        if (Object.keys(i18n.global.messages).includes(response.data.language)) {
          // @ts-ignore
          i18n.global.locale = response.data.language
        }
        setup.value = uiSetup
      }
    } catch (error) { }
  }

  onMounted(async () => {
    await initializeUI();
  });

  return {
    initializeUI,
    setup
  }

}