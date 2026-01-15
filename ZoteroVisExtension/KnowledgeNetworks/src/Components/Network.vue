<script setup lang="ts">
import * as d3 from "d3";
import { ref } from 'vue'
import getData from '../ZoteroAPI/GetData'
const d3Ref = ref('d3Ref');
let d3Instance;
const svgObject = ref<SVGElement | null>(null);

function instantiateGraph(){
  d3Instance = d3.select(svgObject.value);
  d3Instance.select('*').remove();
  d3Instance.html('');
  d3Instance.attr('width', 900)
    .attr('height', 400)
    .append("g")
    .attr('class', 'main-d3-group')
}
instantiateGraph();
getData();
</script>

<template>
 <div>

 </div>
</template>

<style scoped></style>
