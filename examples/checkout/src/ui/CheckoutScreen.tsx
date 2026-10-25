// One screen for every role and viewport; variants are props, not copied files (UI-004).
import { Button, Money, QuantityField, Stack } from "@acme/design-system";
import { CheckoutState, totalCents } from "./state/checkoutStore";

type Props = {
  state: CheckoutState;
  dispatch: (a: any) => void;
  variant?: "shopper" | "agentAssisted";
};

export function CheckoutScreen({ state, dispatch, variant = "shopper" }: Props) {
  return (
    <Stack gap="md">
      {state.lines.map((l) => (
        <QuantityField
          key={l.sku}
          label={`Quantity for ${l.sku}`}
          value={l.qty}
          disabled={state.status !== "editing"}
          onChange={(qty) => dispatch({ type: "setQty", sku: l.sku, qty })}
        />
      ))}
      <Money cents={totalCents(state)} />
      <Button
        onPress={() => dispatch({ type: "submit" })}
        disabled={state.status !== "editing"}
      >
        {variant === "agentAssisted" ? "Charge customer" : "Pay now"}
      </Button>
    </Stack>
  );
}
