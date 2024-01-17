
import { ref, watch } from "vue";
import { useUI } from "./use-ui";

const filtersSelections = ref<Record<string, any[]>>({});
const knowledgeBankSelection = ref<string|null>(null);


export function useSettings() {
    
    return {
        filtersSelections,
        knowledgeBankSelection
    }
}