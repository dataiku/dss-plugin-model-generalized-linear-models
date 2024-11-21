<template>
    <div>
    <q-card-section>
                <h5>Feature Handling</h5>
            </q-card-section>
            <q-card class="q-pa-xl">
                <div v-for="(column, index) in filteredColumns" class="column-management row-spacing">
                    <div class="column-name-container">
                        <h6 class="column-name">{{ store.abbreviateColumnName(column.name) }}</h6>
                    </div>
                    <div class="checkbox-container">
                        <BsCheckbox v-model="column.isIncluded" label="Include?" class="custom-label-spacing"></BsCheckbox>
                    </div>
                    <div class="radio-group-container">
                        <div class="q-gutter-sm row items-center">
                            <q-radio v-model="column.type as any" val="numerical" label="Numerical" />
                        </div>
                        <div class="q-gutter-sm row items-center">
                            <q-radio v-model="column.type as any" val="categorical" label="Categorical" />
                        </div>
                    </div>
                    <div class="radio-group-container">
                        <div class="q-gutter-sm row items-center">
                            <BsSelect
                                label=""
                                :modelValue="column.baseLevel"
                                :all-options="column.options"
                                @update:modelValue="value => column.baseLevel = value">
                            </BsSelect>
                        </div>
                    </div>
                </div>
                
            </q-card>
            <q-card-section>
                <h5>Variable Interactions</h5>
            </q-card-section>
            <q-card class="q-pa-xl">
            <VariableInteractions
                :filtered-columns="filteredColumns"
                :initial-interactions="store.previousInteractions"
                 @update:interactions="store.updateInteractions"
            />
            </q-card>
        </div>
</template>