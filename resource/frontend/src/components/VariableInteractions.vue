<template>
    <div class="interactions-container">
      <div v-if="interactions.length === 0" class="add-initial">
        <q-btn 
          color="primary" 
          class="q-mt-md"
          label="Add an interaction?" 
          @click="addInteraction"
        />
      </div>
      
      <div v-else class="interactions-list">
        <!-- Headers -->
        <div class="interaction-header-row">
          <div class="interaction-label">Interaction</div>
          <div class="variable-header">Variable 1</div>
          <div class="variable-header">Variable 2</div>
          <div class="action-header"></div>
        </div>
  
        <div v-for="(interaction, index) in interactions" :key="index" class="interaction-row">
          <div class="interaction-label">Interaction {{ index + 1 }}</div>
          <BsSelect
            :modelValue="interaction.first"
            class="interaction-select"
            :all-options="filteredColumns.map(col => col.name)"
            @update:modelValue="value => updateInteraction(index, 'first', value)"
            placeholder="Select first variable"
          />
  
          <BsSelect
            :modelValue="interaction.second"
            class="interaction-select"
            :all-options="filteredColumns.map(col => col.name)"
            @update:modelValue="value => updateInteraction(index, 'second', value)"
            placeholder="Select second variable"
          />
  
          <q-btn 
            color="negative" 
            flat
            icon="mdi-delete"
            class="remove-btn"
            @click="removeInteraction(index)"
          >
            <BsTooltip>Remove interaction</BsTooltip>
          </q-btn>
        </div>
  
        <q-btn 
          color="primary" 
          class="q-mt-md"
          label="Add another interaction" 
          @click="addInteraction"
        />
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'VariableInteractions',
    
    props: {
      filteredColumns: {
        type: Array,
        required: true
      },
      initialInteractions: {
        type: Array,
        default: () => []
      }
    },
  
    data() {
      return {
        interactions: [],
        internalUpdate: false,
        lastEmittedInteractions: []
      }
    },
  
    watch: {
      initialInteractions: {
        handler(newInteractions) {
          if (!this.internalUpdate && JSON.stringify(newInteractions) !== JSON.stringify(this.lastEmittedInteractions)) {
            console.log("Initial interactions updated:", newInteractions);
            if (newInteractions && newInteractions.length > 0) {
              this.interactions = newInteractions.map(interaction => ({
                first: interaction.first || '',
                second: interaction.second || ''
              }));
            } else {
              this.interactions = [];
            }
            this.lastEmittedInteractions = newInteractions;
          }
        },
        deep: true
      }
    },
  
    created() {
      if (this.initialInteractions && this.initialInteractions.length > 0) {
        this.interactions = this.initialInteractions.map(interaction => ({
          first: interaction.first || '',
          second: interaction.second || ''
        }));
        this.lastEmittedInteractions = this.initialInteractions;
      }
    },
  
    methods: {
      addInteraction() {
        this.internalUpdate = true;
        try {
          this.interactions.push({
            first: '',
            second: ''
          });
        } finally {
          this.internalUpdate = false;
        }
      },
  
      removeInteraction(index) {
        this.internalUpdate = true;
        try {
          this.interactions.splice(index, 1);
          this.emitUpdate();
        } finally {
          this.internalUpdate = false;
        }
      },
  
      updateInteraction(index, field, value) {
        this.internalUpdate = true;
        try {
          this.interactions[index][field] = value;
          this.emitUpdate();
        } finally {
          this.internalUpdate = false;
        }
      },
  
      emitUpdate() {
        const completeInteractions = this.interactions
          .filter(interaction => interaction.first && interaction.second)
          .map(interaction => ({
            first: interaction.first,
            second: interaction.second
          }));
        
        this.lastEmittedInteractions = completeInteractions;
        
        const formattedInteractions = completeInteractions
          .map(interaction => `${interaction.first}:${interaction.second}`);
        
        this.$emit('update:interactions', formattedInteractions);
      }
    }
  }
  </script>
  
  <style scoped>
  .interactions-container {
    padding: 1rem;
  }
  
  .interaction-header-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: center;
    font-weight: 600;
    color: #666;
    padding: 0 0.5rem;
  }
  
  .interaction-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: center;
  }
  
  .interaction-label {
    width: 100px;
    font-weight: 500;
    color: #666;
  }
  
  .variable-header {
    width: 200px;
    padding: 0 0.5rem;
  }
  
  .action-header {
    width: 40px;
  }
  
  .interaction-select {
    width: 200px;
    flex-shrink: 0;
  }
  
  .remove-btn {
    width: 40px;
    flex-shrink: 0;
  }
  
  .add-initial {
    text-align: center;
    padding: 2rem;
  }
  
  :deep(.q-btn) {
    text-transform: none;
  }
  </style>