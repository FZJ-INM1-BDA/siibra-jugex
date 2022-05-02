<svelte:options accessors={true} />

<div class="container">
  <div class="slider">
    <Slider
      bind:value={permutations}
      min={100}
      max={10000}
      step={1}
      on:SMUISlider:change={update}
      />
  </div>
  <div class="input">
    <Textfield
      class="input"
      bind:value={permutations}
      type="number"/>
  </div>
</div>


<script>
  import Slider from "@smui/slider"
  import Textfield from '@smui/textfield';
  import { createEventDispatcher } from "svelte"
  let permutations = 1000
  const dispatcher = createEventDispatcher()
  function update(){
    dispatcher("PermutationUpdated", permutations)
  }
</script>

<style>
  .container
  {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }

  .container > .slider
  {
    flex: 12rem 0 0;
  }

  .container > .input
  {
    flex: 6rem 0 0;
  }

</style>