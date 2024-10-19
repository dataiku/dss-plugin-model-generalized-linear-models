<template>
    <div class="variable-select-container">
      <BsButton @click="addInteraction" class="q-mt-md" label="Add Interaction" />
      <QCard v-if="interactions.length > 0" class="q-mt-md">
        <QCardSection v-for="(interaction, index) in interactions" :key="index">
          <div class="row q-col-gutter-md">
            <div class="col-5">
              <BsSelect
                v-model="interaction.first"
                :all-options="columnOptions"
                style="min-width: 150px"
              />
            </div>
            <div class="col-5">
              <BsSelect
                label=""
                v-model="interaction.second"
                :all-options="columnOptions"
                style="min-width: 150px"
              />
            </div>
            <div class="col-2">
              <BsButton @click="removeInteraction(index)" label="Remove" />
            </div>
          </div>
        </QCardSection>
      </QCard>
      <div v-else class="q-mt-md">No interactions added yet.</div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import type { PropType } from 'vue';
  import { BsButton, BsSelect } from 'quasar-ui-bs';
  import { QCard, QCardSection } from 'quasar';
  import cloneDeep from 'lodash/cloneDeep';

  interface Column {
    name: string;
    // Add other properties if needed
  }
  
  interface Interaction {
    first: string;
    second: string;
  }
  
  export default defineComponent({
    name: 'VariableInteractions',
    components: {
      BsButton,
      BsSelect,
      QCard,
      QCardSection
    },
    props: {
      filteredColumns: {
        type: Array as PropType<Column[]>,
        required: true
      },
      initialInteractions: {
      type: Array as PropType<Interaction[]>,
      default: () => []
    }
    },
    data() {
      return {
        interactions: [] as Interaction[]
      };
    },
    computed: {
      columnOptions(): string[] {
        return this.filteredColumns.map(column => column.name);
      },
      formattedInteractions(): string[] {
        console.log("Formatting interactions to return");
        return this.interactions.map(interaction => {
            // Check if the interaction is already in the correct format
            if (typeof interaction === 'string' && interaction.includes(':')) {
            return interaction;
            }
            // If it's not, format it
            if (interaction.first && interaction.second) {
            return `${interaction.first}:${interaction.second}`;
            }
            // If it's neither in the correct format nor has the expected properties, return it as is
            return String(interaction);
        });
        }
    },
    methods: {
      addInteraction() {
        console.log("Triggering addition of a new interactions")
        this.interactions.push({ first: '', second: '' })
        console.log("New interactions",this.interactions);
      },
      removeInteraction(index: number) {
        this.interactions.splice(index, 1);
      }
    },
    created() {
    console.log("Initalising")
    this.interactions = cloneDeep(this.initialInteractions);

    },
    watch: {
      interactions: {
        handler(newInteractions: Interaction[]) {
        console.log("Changes to interactions detected in the child as:",newInteractions)
        this.$emit('update:interactions', this.formattedInteractions);
        },
        deep: true
      },
      initialInteractions: {
      handler(newInteractions: Interaction[]) {
        console.log("Inital interactions are being set:",newInteractions)
        if (JSON.stringify(this.interactions) !== JSON.stringify(newInteractions)) {
          this.interactions = cloneDeep(JSON.parse(JSON.stringify(newInteractions)));
        }
      }
    },  
        
    }
  });
  </script>
  
  <style scoped>
  .interaction-variables {
    padding: 20px;
  }
  .variable-select-container {
    margin-top: 20px;
  }
  </style>