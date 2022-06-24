<svelte:options accessors={true} />

<div class="container">
  <div class="slider">
    <Slider
      bind:value={value}
      {min}
      {max}
      {step}
      on:SMUISlider:change={update}
      />
  </div>
  <div class="input">
    <Textfield
      class="input"
      bind:value={value}
      type="number"/>
  </div>
</div>


<script>
  import Slider from "@smui/slider"
  import Textfield from '@smui/textfield';
  import { createEventDispatcher } from "svelte"
  export let min = 0;
  export let max = 1;
  export let step = 0.01;
  export let value = 0;
  const dispatcher = createEventDispatcher()
  function update(){
    dispatcher("ValueUpdated", value)
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