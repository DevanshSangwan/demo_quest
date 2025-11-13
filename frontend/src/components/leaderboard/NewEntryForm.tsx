import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useUpdateScore } from "@/hooks/queries/useLeaderboardQueries";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

const formSchema = z.object({
  userId: z.string().min(1, "User ID is required").trim(),
  delta: z
    .string()
    .trim()
    .refine((value) => value !== "", { message: "Score adjustment is required" })
    .refine((value) => !Number.isNaN(Number(value)), {
      message: "Score adjustment must be a number",
    }),
});

type FormValues = z.infer<typeof formSchema>;

export const NewEntryForm = () => {
  const mutation = useUpdateScore();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      userId: "",
      delta: "",
    },
  });

  const onSubmit = (values: FormValues) => {
    const deltaValue = Number(values.delta);
    if (Number.isNaN(deltaValue)) {
      form.setError("delta", { message: "Score adjustment must be a number" });
      return;
    }

    mutation.reset();
    mutation.mutate(
      {
        user_id: values.userId,
        delta: deltaValue,
      },
      {
        onSuccess: () => {
          form.reset({ userId: "", delta: "" });
        },
      }
    );
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="userId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>User ID</FormLabel>
              <FormControl>
                <Input placeholder="Enter the user ID" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="delta"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Score Adjustment</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="Enter score adjustment"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Submitting..." : "Apply Update"}
        </Button>
        {mutation.isError && (
          <p className="text-sm text-destructive">
            Unable to apply the update. Please try again.
          </p>
        )}
        {mutation.isSuccess && (
          <p className="text-sm text-muted-foreground">Score updated successfully.</p>
        )}
      </form>
    </Form>
  );
};
