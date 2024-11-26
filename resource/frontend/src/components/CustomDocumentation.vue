<template>
    <BsDocumentation>
        <template #title>
            <img :src="docLogo" style="margin-right: 12px;"/>
            Parameters Analyzer
        </template>

        <template #content>
            <div class="bs-font-medium-3-normal">
                <p>
                    The Parameters Analyzer solution helps you understand your
                    historical process performance.<br />
                    Engineers and Technicians can identify and analyze easily
                    your key target process parameters. <br />
                    Find and set up ranges for those parameters to improve your
                    outcome.
                </p>
                <p>
                    Within the Web App of Parameters Analyzer, you can perform a
                    complete analysis of your historical performance and
                    understand how to improve it:
                </p>
                <ul>
                    <li>Define your “good” target.</li>
                    <li>Analyze parameters' impact.</li>
                    <li>Set main parameters and ranges`</li>
                </ul>
            </div>
        </template>
    </BsDocumentation>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import docLogo from "../assets/images/doc-logo-example.svg";

export default defineComponent({
    data() {
        return {
            docLogo,
        }
    }
})
</script>
